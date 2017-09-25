from flask import Blueprint
from pprint import pprint
from flask import jsonify
from flask import request
from auth import Auth
from regions import Region
import json
from googleapiclient import errors

disks = Blueprint('disks', __name__)


# function interface for google API
def gcp_disk_func(func_name, param):
    service = param['service']
    project = param['project']
    zone = param['zone']

    if func_name == "disk_insert":
        import rstr
        disk_list=gcp_disk_func("disk_list",param)
        while True:
            name = rstr.xeger('[a-z](?:[-a-z0-9]{0,61}[a-z0-9])?')
            if name not in disk_list:
                break
        disk_body = {
            "name": name,
            "sizeGb": param['sizeGb'],
            "storageType": param['storageType']
        }

        myrequest = service.disks().insert(project=project, zone=zone, body=disk_body)
        myresponse = myrequest.execute()
        res={
            'id':myresponse['targetId'],
            'status':myresponse['status'],
            'name':myresponse['targetLink'].split('/disks/')[1],
        }
        return res
    
    if func_name=="disk_list":
        myrequest = service.disks().list(project=project, zone=zone)
        disk_list=[]
        while myrequest is not None:
            myresponse = myrequest.execute()
            for disk in myresponse['items']:
                # TODO: Change code below to process each `disk` resource:
                disk_list.append(disk['name'])

            myrequest = service.disks().list_next(previous_request=myrequest, previous_response=myresponse)
        return disk_list

    if func_name=="disk_info":
        disk=param['disk_name']
        myrequest = service.disks().get(project=project, zone=zone, disk=disk)
        myresponse = myrequest.execute()
        res={
            'id':myresponse['id'],
            'create_time':myresponse['creationTimestamp'],
            'size':myresponse['sizeGb'],
            'status':myresponse['status'],
            'type':myresponse['type'].split('/diskTypes/')[1]
        }
        return res