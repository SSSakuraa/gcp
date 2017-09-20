from flask import Blueprint
from pprint import pprint
from flask import jsonify
from flask import request
from auth import Auth
import json

from googleapiclient import errors

instances=Blueprint('instances',__name__)

def get_machine_type(myresponse):
    return myresponse['machineType'][myresponse['machineType'].index('machineTypes/')+len('machineTypes/'):]





@instances.route('/servers/<instance>',methods=['GET'])
def instance_getinfo(instance):
    try:

        auth=Auth()
        service=auth.get_service(request)
        zone=auth.region+'-'+request.args.get('zone')
        param = {
                'project':auth.project,
                'zone':zone,
                'instance':instance,
                'service':service,
        }
        
        return jsonify(gcp_func("server_get",param))
    except errors.HttpError as e:
        msg=json.loads(e.content)
        return jsonify(msg=msg),msg['error']['code']


@instances.route('/servers',methods=['POST'])
def instance_create():
    try:
        auth=Auth()
        service=auth.post_service(request)
        data=json.loads(request.get_data())
        name=data['name']
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
                            "diskName":name,
                            "sourceImage": "projects/debian-cloud/global/images/debian-9-stretch-v20170829"
                            }
                        }
                    ]                                                
                }
        pprint(auth.project)
        myrequest=service.instances().insert(project=auth.project,zone=auth.zone,body=instance_body)
        myresponse=myrequest.execute()
        pprint(myresponse)
        res=json.dumps(myresponse,indent=4)
        return res
    except errors.HttpError as e:
        msg=json.loads(e.content)
        return jsonify(msg=msg),msg['error']['code']

def gcp_func(func_name, param):
    service=param['service']
    project=param['project']
    zone=param['zone']
    instance=param['instance']
    
    if func_name =="server_get":
        
        myrequest=service.instances().get(project=project, zone=zone, instance=instance)
        myresponse = myrequest.execute()
        status={
                'TERMINATED':'stopped',
                'RUNNING':'running',
                'STOPPING':'stopping'

                }
        accessConfig=myresponse["networkInterfaces"][0]["accessConfigs"][0]
        if accessConfig.has_key('natIP'):
            eip=accessConfig['natIP']
        else:
            eip=""
        res={
                "id":myresponse["id"],
                "launch_time":myresponse["creationTimestamp"],
                "region":myresponse["zone"][myresponse["zone"].index("zones")+len("zones/"):len(myresponse['zone'])-2],
                "ip":myresponse["networkInterfaces"][0]["networkIP"],
                "os":myresponse["disks"][0]["licenses"][0][myresponse["disks"][0]["licenses"][0].index("licenses/")+len("licenses/"):],
                "image":myresponse["disks"][0]["licenses"][0],
                "instance_type":myresponse["machineType"][myresponse["machineType"].index("machineTypes/")+len("machineTypes/"):],
                "eip":eip,
                "status_check":"", # TODO
                "state":status[myresponse["status"]]
                
                }
        return res

    if func_name=="server_off":
        myrequest=service.instances().stop(project=project,zone=zone,instance=instance)
        myresponse=myrequest.execute()
        res={
                'id':myresponse['id'],
                'state':myresponse['status']
                }
        return res

    if func_name=='server_on':
        myrequest=service.instances().start(project=project,zone=zone,instance=instance)
        myresponse=myrequest.execute()
        res={
                'id':myresponse['id'],
                'state':myresponse['status']
                }
        return res

    if func_name=="server_delete":
        myrequest=service.instances().stop(project=project,zone=zone,instance=instance)
        myresponse=myrequest.execute()
        res={
                'id':myresponse['id'],
                'state':myresponse['status']
                }
        return res
    
    if func_name=="server_modify":
        myrequest=service.instances().setMachineType(project=project,zone=zone,instance=instance,body=param['body'])
        myresponse=myrequest.execute()
        pprint(myresponse)
        res={
                'id':myresponse['id'],
                'state':myresponse['status']
                }
        return res
    if func_name=="server_reboot":       
        gcp_func("server_off",param)
        inst_info=gcp_func("server_get",param)
        status=inst_info['state']
        while status !='stopped':
            status=gcp_func("server_get",param)['state']
            #print status
        res=gcp_func("server_on",param)
        return res
    
    return "haha"


@instances.route('/servers/<instance>',methods=['POST'])
def operation(instance):
    try:
        auth=Auth()
        service=auth.post_service(request)
        data=json.loads(request.get_data())
        zone=auth.region+'-'+data['zone']
        action=data['action']
        param = {
                'project':auth.project,
                'zone':zone,
                'instance':instance,
                'service':service,

                }
        pprint(action)
        if action=="server_off": 
            return jsonify(gcp_func("server_off",param))

        if action=='server_on':
            return jsonify(gcp_func('server_on',param))

        if action=='server_delete':
            return jsonify(gcp_func('server_delete',param))

        if action=='server_reboot':
            return jsonify(gcp_func('server_reboot',param))

        if action=='server_modify':
            inst_info=gcp_func("server_get",param)
            status=inst_info['state']
            origin_type=inst_info['instance_type']
            machine_type='zones/'+zone+'/machineTypes/'+data['dst_inst_type']
            body={
                    'machineType':machine_type
                    }

            if status != 'stopped':
                gcp_func("server_off",param)
                while status !='stopped':
                    status=gcp_func("server_get",param)['state']
                    #print status

            param['body']=body
            gcp_func("server_modify",param)
            
            gcp_func('server_on',param)

            myresponse=gcp_func('server_get',param)

            res={
                    'id':myresponse['id'],
                    'origin_inst_type':origin_type,
                    'current_inst_type':myresponse['instance_type']
                    }
            return jsonify(res)
        res="operation "+action+" not found"
        return jsonify(msg=res),404
    except errors.HttpError as e:
        msg=json.loads(e.content)
        return jsonify(msg=msg),msg['error']['code']
