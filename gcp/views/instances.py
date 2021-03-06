import json
from pprint import pprint

from flask import Blueprint
from flask import jsonify
from flask import request
from auth import Auth
from googleapiclient import errors

from regions import Region
from networks import gcp_network_func
from disks import gcp_disk_func


instances = Blueprint('instances', __name__)

# get server information with instance-name
@instances.route('/servers/<instance>', methods=['GET'])
def instance_getinfo(instance):
    try:
        auth = Auth()
        service = auth.get_service(request)
        zone = auth.region + '-' + request.args.get('zone')
        param = {
            'project': auth.project,
            'zone': zone,
            'instance': instance,
            'service': service,
        }
        return jsonify(gcp_instance_func("server_get", param))
    except errors.HttpError as e:
        msg = json.loads(e.content)
        return jsonify(msg=msg['error']['message']), msg['error']['code']


@instances.route('/servers', methods=['POST'])
def instance_create():
    try:
        auth = Auth()
        service = auth.post_service(request)
        data = json.loads(request.get_data())
        zone = auth.region + '-' + data['zone']
        param = {
            'project': auth.project,
            'zone': zone,
            'service': service,
            'vpc_id': data['vpc_id'],
            'subnet_cidr': data['subnet_cidr']
        }
        network = gcp_network_func("find_network", param)
        if data['subnet_cidr'] is not None and data['subnet_cidr'] != "":
            subnet_cidr = gcp_network_func("find_subnetwork", param)

        access_configs = []
        if data['eip_enable'] == 1:
            access_configs.append({})

        
        quantity = data['quantity']
        disks_info = []
        param['ebs']=data['ebs']
        while quantity > 0:
            quantity = quantity - 1
            instance_disk=gcp_disk_func("disk_insert_batch",param)
            disks_info.append(instance_disk)

        batch_res = []
        quantity = data['quantity']
        index = 0
        while index < quantity:
            try:
                import rstr
                instance_list = gcp_instance_func("server_list", param)
                while True:
                    name = rstr.xeger('[a-z](?:[-a-z0-9]{0,61}[a-z0-9])?')
                    if name not in instance_list:
                        break
                pprint(name)

                # create disks for each instance
                disks = []
                msg = []
                disks.append({
                    "boot": "true",
                            "autoDelete": "true",
                            "initializeParams": {
                                "sourceImage": data['image'],
                            }
                })
                instance_disk = disks_info[index]
                index = index + 1
                for disk in instance_disk:
                    if 'error' in disk:
                        msg.append('error while creating disk ' + disk['index']+' for ' +
                                   name + ': ' + disk['error'])
                    else:
                        disk_param = {
                            'project': auth.project,
                            'zone': zone,
                            'service': service,
                            'disk_name': disk['disk_name']
                        }
                        while True:
                            if gcp_disk_func("disk_info", disk_param)['status'] == 'READY':
                                break

                        disks.append({
                            'source': "/projects/" + auth.project + "/zones/" + zone + "/disks/" + disk['disk_name']
                        })

                instance_body = {
                    # TODO: Add desired entries to the request body.
                    "machineType": "zones/" + zone + "/machineTypes/" + data['instance_type'],
                    "name": name,
                    "networkInterfaces": [
                        {
                            "network": "projects/" + auth.project + "/global/networks/" + network['name'],
                            "accessConfigs": access_configs
                        }
                    ],
                    "disks": disks,
                    "labels": data['tags']
                }
                myrequest = service.instances().insert(
                    project=auth.project, zone=zone, body=instance_body)
                myrequest.execute()
                param['instance'] = name
                while True:
                    instance_info = gcp_instance_func('server_get', param)
                    if instance_info['ip'] != []:
                        if data['eip_enable'] == 1 and instance_info['eip'] != "":
                            break
                        if data['eip_enable'] == 0:
                            break

                res = {
                    'status': 'success',
                    'msg': msg,
                    'ip': instance_info['ip'],
                    'id': instance_info['id'],
                    'name': name,
                    'eip': instance_info['eip'],
                    'launch_time': instance_info['launch_time']
                }
                batch_res.append(res)
            except errors.HttpError as e:
                msg = json.loads(e.content)
                batch_res.append(
                    {'msg': msg['error']['message'],
                     'code': msg['error']['code']
                     })
        return jsonify(items=batch_res, total=len(batch_res))
    except errors.HttpError as e:
        msg = json.loads(e.content)
        return jsonify(msg=msg['error']['message']), msg['error']['code']


# server operation with instance-name
@instances.route('/servers/<instance>', methods=['POST'])
def instance_operation(instance):
    try:
        auth = Auth()
        service = auth.post_service(request)
        data = json.loads(request.get_data())
        zone = auth.region + '-' + data['zone']
        action = data['action']
        param = {
            'project': auth.project,
            'zone': zone,
            'instance': instance,
            'service': service,
        }
        if action == "server_off":
            res_get = gcp_instance_func('server_get', param)
            res = {
                'id': res_get['id'],
                'state': res_get['state']
            }
            if not data['dry_run']:
                gcp_instance_func("server_off", param)
                res['state'] = gcp_instance_func('server_get', param)['state']
            return jsonify(res)

        if action == 'server_on':
            res_get = gcp_instance_func('server_get', param)
            res = {
                'id': res_get['id'],
                'state': res_get['state']
            }
            if not data['dry_run']:
                gcp_instance_func("server_on", param)
                res['state'] = gcp_instance_func('server_get', param)['state']
            return jsonify(res)

        # TODO : do not get after delete
        if action == 'server_delete':
            res_get = gcp_instance_func('server_get', param)
            res = {
                'id': res_get['id'],
                'state': res_get['state']
            }
            if not data['dry_run']:
                gcp_instance_func("server_delete", param)
                res['state'] = gcp_instance_func('server_get', param)['state']
            return jsonify(res)

        # TODO : while in reboot
        if action == 'server_reboot':
            res_get = gcp_instance_func('server_get', param)
            res = {
                'id': res_get['id'],
                'state': res_get['state']
            }
            if not data['dry_run']:
                gcp_instance_func("server_reboot", param)
                res['state'] = gcp_instance_func('server_get', param)['state']
            return jsonify(res)

        if action == 'server_modify':
            inst_info = gcp_instance_func("server_get", param)
            origin_type = inst_info['instance_type']
            res = {
                'id': inst_info['id'],
                'origin_inst_type': origin_type,
                'current_inst_type': inst_info['instance_type']
            }
            if not data['dry_run']:
                status = inst_info['state']
                if status != 'stopped':
                    return jsonify(msg="The instance is not STOPPED!"), 409

                machine_type = 'zones/' + zone + \
                    '/machineTypes/' + data['dst_inst_type']
                body = {
                    'machineType': machine_type
                }
                param['body'] = body
                gcp_instance_func("server_modify", param)
                myresponse = gcp_instance_func('server_get', param)
                res['current_inst_type'] = gcp_instance_func(
                    'server_get', param)['instance_type']
            return jsonify(res)

        # if action == 'server_rebind':
        #     return jsonify(msg="server_rebind not supported"), 404

        res = "operation " + action + " not supported yet."
        return jsonify(msg=res), 404
    except errors.HttpError as e:
        msg = json.loads(e.content)
        return jsonify(msg=msg['error']['message']), msg['error']['code']

# servers batch operations


@instances.route('/server/batch', methods=['POST'])
def batch_operation():
    try:
        auth = Auth()
        service = auth.post_service(request)
        data = json.loads(request.get_data())
        zone = auth.region + '-' + data['zone']
        action = data['action']
        param = {
            'project': auth.project,
            'zone': zone,
            'service': service,
        }

        instance_list = data['instances']
        batch_res = []
        for instance in instance_list:
            try:
                param['instance'] = instance
                if action == "server_off":
                    res_get = gcp_instance_func('server_get', param)
                    res = {
                        'id': res_get['id'],
                        'state': res_get['state']
                    }
                    if not data['dry_run']:
                        gcp_instance_func("server_off", param)
                        res['state'] = gcp_instance_func(
                            'server_get', param)['state']
                    batch_res.append(res)

                if action == 'server_on':
                    res_get = gcp_instance_func('server_get', param)
                    res = {
                        'id': res_get['id'],
                        'state': res_get['state']
                    }
                    if not data['dry_run']:
                        gcp_instance_func("server_on", param)
                        res['state'] = gcp_instance_func(
                            'server_get', param)['state']
                    batch_res.append(res)

                # TODO : do not get after delete
                if action == 'server_delete':
                    res_get = gcp_instance_func('server_get', param)
                    res = {
                        'id': res_get['id'],
                        'state': res_get['state']
                    }
                    if not data['dry_run']:
                        gcp_instance_func("server_delete", param)
                        res['state'] = gcp_instance_func(
                            'server_get', param)['state']
                    batch_res.append(res)

                # TODO : while in reboot
                if action == 'server_reboot':
                    res_get = gcp_instance_func('server_get', param)
                    res = {
                        'id': res_get['id'],
                        'state': res_get['state']
                    }
                    if not data['dry_run']:
                        gcp_instance_func("server_reboot", param)
                        res['state'] = gcp_instance_func(
                            'server_get', param)['state']
                    batch_res.append(res)

                if action == 'server_modify':
                    inst_info = gcp_instance_func("server_get", param)
                    origin_type = inst_info['instance_type']
                    res = {
                        'id': inst_info['id'],
                        'origin_inst_type': origin_type,
                        'current_inst_type': inst_info['instance_type']
                    }
                    if not data['dry_run']:
                        status = inst_info['state']
                        if status != 'stopped':
                            return jsonify(msg="The instance is not STOPPED!"), 409

                        machine_type = 'zones/' + zone + \
                            '/machineTypes/' + data['dst_inst_type']
                        body = {
                            'machineType': machine_type
                        }
                        param['body'] = body
                        gcp_instance_func("server_modify", param)
                        myresponse = gcp_instance_func('server_get', param)
                        res['current_inst_type'] = gcp_instance_func(
                            'server_get', param)['instance_type']
                    batch_res.append(res)

            except errors.HttpError as e:
                msg = json.loads(e.content)
                batch_res.append(
                    {'msg': msg['error']['message'],
                     'code': msg['error']['code']
                     })

        return jsonify(res=batch_res, total=len(batch_res))
    except errors.HttpError as e:
        msg = json.loads(e.content)
        return jsonify(msg=msg['error']['message']), msg['error']['code']


@instances.route('/server/batch', methods=['GET'])
def batch_info():
    try:
        auth = Auth()
        service = auth.get_service(request)
        zone = auth.region + '-' + request.args.get('zone')
        param = {
            'project': auth.project,
            'zone': zone,
            'service': service,
        }
        instance_list = list(eval(request.args.get('instances')))
        batch_res = []
        for instance in instance_list:
            try:
                param['instance'] = instance
                res = gcp_instance_func("server_get", param)
                batch_res.append(res)
            except errors.HttpError as e:
                msg = json.loads(e.content)
                batch_res.append(
                    {'msg': msg['error']['message'],
                     'code': msg['error']['code']
                     })
        return jsonify(items=batch_res, total=len(batch_res))
    except errors.HttpError as e:
        msg = json.loads(e.content)
        return jsonify(msg=msg['error']['message']), msg['error']['code']


@instances.route('/fee', methods=['GET'])
def instances_fee():
    try:
        from gcp import fee
        auth = Auth()
        auth.get_service(request)
        data = request.args.to_dict()
        ebs = list(eval(data['ebs']))
        instance_type = data['instance_type']
        os = data['os']

        quantity = int(data['quantity'])
        total_compute = round(fee.instance_price[instance_type]['price'][Region(
        ).get_region_name(auth.region)] * quantity, 2)
        total_ebs = 0
        for each_ebs in ebs:
            total_ebs += round(fee.disk_price[each_ebs['type']][Region(
            ).get_region_name(auth.region)] * int(each_ebs['size']), 2)
        total = total_compute + total_ebs
        res = {
            'compute': total_compute,
            'ebs': total_ebs,
            'total': total
        }
        return jsonify(res)
    except errors.HttpError as e:
        msg = json.loads(e.content)
        return jsonify(msg=msg['error']['message']), msg['error']['code']

# for test only
@instances.route('/state', methods=['GET'])
def instance_state():
    try:
        auth = Auth()
        service = auth.get_service(request)
        data = request.args.to_dict()
        zone = auth.region + '-' + data['zone']
        param = {
            'project': auth.project,
            'zone': zone,
            'instance': data['instance'],
            'service': service,
        }
        while True:
            status = gcp_instance_func("server_get", param)['state']
            pprint(status)

        return jsonify("res")
    except errors.HttpError as e:
        msg = json.loads(e.content)
        return jsonify(msg=msg['error']['message']), msg['error']['code']


# function interface for google API
def gcp_instance_func(func_name, param):
    status = {
        'TERMINATED': 'stopped',
        'RUNNING': 'running',
        'STOPPING': 'stopping',
        'PROVISIONING': 'pending',  # reserving resources for instance
        'STAGING': 'pending'  # preparing for launch

    }

    if func_name == "server_list":
        return gcp_server_list(param)

    if func_name == "server_get":
        param['status'] = status
        return gcp_server_get(param)

    if func_name == "server_off":
        gcp_server_off(param)

    elif func_name == 'server_on':
        gcp_server_on(param)

    elif "server_delete" == func_name:
        gcp_server_delete(param)

    elif "server_modify" == func_name:
        gcp_server_modify(param)

    elif "server_reboot" == func_name:
        gcp_server_reboot(param)

    return


def gcp_server_list(param):
    myrequest = param['service'].instances().list(
        project=param['project'], zone=param['zone'])
    instance_list = []
    while myrequest is not None:
        myresponse = myrequest.execute()
        for instance in myresponse['items']:
            instance_list.append(instance['name'])
        myrequest = param['service'].instances().list_next(
            previous_request=myrequest, previous_response=myresponse)
    return instance_list


def gcp_server_get(param):
    myrequest = param['service'].instances().get(
        project=param['project'], zone=param['zone'], instance=param['instance'])
    myresponse = myrequest.execute()
    status = param['status']
    network_if = myresponse['networkInterfaces']
    ip = []
    eip = ""
    for interface in network_if:
        if 'networkIP' in interface:
            ip.append(interface['networkIP'])
    if 'accessConfigs' in network_if[0]:
        if 'natIP' in network_if[0]['accessConfigs'][0]:
            eip = network_if[0]['accessConfigs'][0]['natIP']
    res = {
        "id": myresponse["id"],
        "launch_time": myresponse["creationTimestamp"],
        "region": myresponse["zone"].split('/zones/')[1],
        "ip": ip,
        "os": myresponse["disks"][0]["licenses"][0].split('/licenses/')[1],
        # TODO  search the disk info in disks
        "image": myresponse["disks"][0]["licenses"][0].split('/licenses/')[1],
        "instance_type": myresponse["machineType"].split('/machineTypes/')[1],
        "eip": eip,
        "status_check": "",  # TODO
        "state": status[myresponse["status"]]
    }
    return res


def gcp_server_off(param):
    myrequest = param['service'].instances().stop(
        project=param['project'], zone=param['zone'], instance=param['instance'])
    myrequest.execute()
    return


def gcp_server_on(param):
    myrequest = param['service'].instances().start(
        project=param['project'], zone=param['zone'], instance=param['instance'])
    myrequest.execute()
    return


def gcp_server_delete(param):
    myrequest = param['service'].instances().delete(
        project=param['project'], zone=param['zone'], instance=param['instance'])
    myrequest.execute()
    return


def gcp_server_modify(param):
    myrequest = param['service'].instances().setMachineType(
        project=param['project'], zone=param['zone'], instance=param['instance'], body=param['body'])
    myrequest.execute()
    return


def gcp_server_reboot(param):
    gcp_instance_func("server_off", param)
    inst_info = gcp_instance_func("server_get", param)
    status = inst_info['state']
    while status != 'stopped':
        status = gcp_instance_func("server_get", param)['state']
    gcp_instance_func("server_on", param)
    return
