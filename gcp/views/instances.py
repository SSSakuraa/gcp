from flask import Blueprint
from pprint import pprint
from flask import jsonify
from flask import request
from auth import Auth
from regions import Region
import json

from googleapiclient import errors

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

        return jsonify(gcp_func("server_get", param))
    except errors.HttpError as e:
        msg = json.loads(e.content)
        return jsonify(msg=msg['error']['message']), msg['error']['code']


@instances.route('/servers', methods=['POST'])
def instance_create():
    try:
        import rstr
        name = rstr.xeger('[a-z](?:[-a-z0-9]{0,61}[a-z0-9])?')

        auth = Auth()
        service = auth.post_service(request)
        data = json.loads(request.get_data())
        name = data['name']
        instance_body = {
            # TODO: Add desired entries to the request body.
            "machineType": "zones/us-west1-a/machineTypes/n1-standard-2",
            "name": name,

            "networkInterfaces": [
                {
                    "name": "nic0",
                    "network": "projects/saintern-175510/global/networks/default",
                    "accessConfigs": [
                            {
                                "name": "External NAT"
                            }
                    ]
                }
            ],
            "disks": [
                {
                    "deviceName": name,
                    "boot": "true",
                    "autoDelete": "true",
                    "initializeParams": {
                            "diskName": name,
                            "sourceImage": "projects/debian-cloud/global/images/debian-9-stretch-v20170829"
                    }
                }
            ]
        }
        pprint(auth.project)
        myrequest = service.instances().insert(
            project=auth.project, zone=auth.zone, body=instance_body)
        myresponse = myrequest.execute()
        pprint(myresponse)
        res = json.dumps(myresponse, indent=4)
        return res
    except errors.HttpError as e:
        msg = json.loads(e.content)
        return jsonify(msg=msg), msg['error']['code']



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
            if data['dry_run']:
                if gcp_func("server_get",param)['state'] =="stopped":
                    return jsonify(msg="The server is already stopped.")
                else:
                    return jsonify(msg="The server is not stopped.")           
            return jsonify(gcp_func("server_off", param))

        if action == 'server_on':
            if data['dry_run']:
                if gcp_func("server_get",param)['state'] =="running":
                    return jsonify(msg="The server is already running.")
                else:
                    return jsonify(msg="The server is not running.")
            return jsonify(gcp_func('server_on', param))

        if action == 'server_delete':
            if data['dry_run']:
                if gcp_func("server_get",param)['state'] =="running":
                    return jsonify(msg="The server is already in use.")
                else:
                    return jsonify(msg="The server is not running.")
            return jsonify(gcp_func('server_delete', param))

        if action == 'server_reboot':
            if data['dry_run']:
                return jsonify(msg="The server is already %s." % gcp_func("server_get",param)['state'] )
            return jsonify(gcp_func('server_reboot', param))

        if action == 'server_modify':           
            inst_info = gcp_func("server_get", param)          
            origin_type = inst_info['instance_type']          

            if data['dry_run']:
                if data['dst_inst_type'] == origin_type:
                    return jsonify(msg="The instance type is already %s" % origin_type)
                return jsonify(msg="The current instance type is %s" % origin_type)
            status = inst_info['state']
            if status != 'stopped':
                return jsonify(msg="The instance is not STOPPED!"), 409
                      
            machine_type = 'zones/' + zone + '/machineTypes/' + data['dst_inst_type']
            body = {
                'machineType': machine_type
            }            
            param['body'] = body
            gcp_func("server_modify", param)
            myresponse = gcp_func('server_get', param)
            res = {
                'id': myresponse['id'],
                'origin_inst_type': origin_type,
                'current_inst_type': myresponse['instance_type']
            }
            return jsonify(res)

        # if action == 'server_rebind':
        #     return jsonify(msg="server_rebind not supported"), 404

        res = "operation " + action + " not supported yet."
        return jsonify(msg=res), 404
    except errors.HttpError as e:
        msg = json.loads(e.content)
        return jsonify(msg=msg['error']['message']), msg['error']['code']

# servers batch operations
@instances.route('/servers/batch', methods=['POST'])
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
                print(instance)
                param['instance'] = instance

                if action == "server_off":
                    res = gcp_func("server_off", param)
                    batch_res.append(res)

                elif action == "server_on":
                    res = gcp_func("server_on", param)
                    batch_res.append(res)

                elif action == 'server_delete':
                    res = gcp_func('server_delete', param)
                    batch_res.append(res)

                elif action == 'server_reboot':
                    res = gcp_func('server_reboot', param)
                    batch_res.append(res)

                elif action == 'server_modify':
                    inst_info = gcp_func("server_get", param)
                    status = inst_info['state']
                    origin_type = inst_info['instance_type']
                    machine_type = 'zones/' + zone + \
                        '/machineTypes/' + data['dst_inst_type']

                    if status != 'stopped':
                        res = {"msg": "The instance is not STOPPED!"}
                        batch_res.append(res)
                        continue
                    body = {
                        'machineType': machine_type
                    }
                    param['body'] = body
                    gcp_func("server_modify", param)

                    myresponse = gcp_func('server_get', param)

                    res = {
                        'id': myresponse['id'],
                        'origin_inst_type': origin_type,
                        'current_inst_type': myresponse['instance_type']
                    }
                    batch_res.append(res)

                elif action == 'server_rebind':
                    res = {'error': "server_rebind not supported"}
                    batch_res.append(res)
                else:
                    res = {'error': "operation " + action + " not found"}
                    batch_res.append(res)

            except errors.HttpError as e:
                batch_res.append(
                    {'error': json.loads(e.content)['error']['message']})

        return jsonify(res=batch_res, total=len(batch_res))
    except errors.HttpError as e:
        msg = json.loads(e.content)
        return jsonify(msg=msg['error']['message']), msg['error']['code']


@instances.route('/servers/batch', methods=['GET'])
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
                res = gcp_func("server_get", param)
                batch_res.append(res)
            except errors.HttpError as e:
                batch_res.append(
                    {'error': json.loads(e.content)['error']['message']})
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
        ebs = list(eval(request.args.get('ebs')))
        instance_type = request.args.get('instance_type')
        os = request.args.get('os')

        quantity = int(request.args.get('quantity'))
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


# function interface for google API
def gcp_func(func_name, param):
    service = param['service']
    project = param['project']
    zone = param['zone']
    instance = param['instance']

    if func_name == "server_get":
        myrequest = service.instances().get(project=project, zone=zone, instance=instance)
        myresponse = myrequest.execute()
        status = {
            'TERMINATED': 'stopped',
            'RUNNING': 'running',
            'STOPPING': 'stopping'

        }
        access_config = myresponse["networkInterfaces"][0]["accessConfigs"][0]
        if 'natIP' in access_config:
            eip = access_config['natIP']
        else:
            eip = ""
        res = {
            "id": myresponse["id"],
            "launch_time": myresponse["creationTimestamp"],
            "region": myresponse["zone"][myresponse["zone"].index("zones") + len("zones/"):len(myresponse['zone']) - 2],
            "ip": myresponse["networkInterfaces"][0]["networkIP"],
            "os": myresponse["disks"][0]["licenses"][0][myresponse["disks"][0]["licenses"][0].index("licenses/") + len("licenses/"):],
            "image": myresponse["disks"][0]["licenses"][0],
            "instance_type": myresponse["machineType"][myresponse["machineType"].index("machineTypes/") + len("machineTypes/"):],
            "eip": eip,
            "status_check": "",  # TODO
            "state": status[myresponse["status"]]

        }
        return res

    if func_name == "server_off":
        myrequest = service.instances().stop(
            project=project, zone=zone, instance=instance)
        myresponse = myrequest.execute()
        res = {
            'id': myresponse['id'],
            'state': myresponse['status']
        }
        return res

    if func_name == 'server_on':
        myrequest = service.instances().start(
            project=project, zone=zone, instance=instance)
        myresponse = myrequest.execute()
        res = {
            'id': myresponse['id'],
            'state': myresponse['status']
        }
        return res

    if func_name == "server_delete":
        myrequest = service.instances().delete(
            project=project, zone=zone, instance=instance)
        myresponse = myrequest.execute()
        res = {
            'id': myresponse['id'],
            'state': myresponse['status']
        }
        return res

    if func_name == "server_modify":
        myrequest = service.instances().setMachineType(
            project=project, zone=zone, instance=instance, body=param['body'])
        myresponse = myrequest.execute()
        pprint(myresponse)
        res = {
            'id': myresponse['id'],
            'state': myresponse['status']
        }
        return res

    if func_name == "server_reboot":
        gcp_func("server_off", param)
        inst_info = gcp_func("server_get", param)
        status = inst_info['state']
        while status != 'stopped':
            status = gcp_func("server_get", param)['state']
        res = gcp_func("server_on", param)
        return res

    return
