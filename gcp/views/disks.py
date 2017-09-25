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
        name = rstr.xeger('[a-z](?:[-a-z0-9]{0,61}[a-z0-9])?')
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
