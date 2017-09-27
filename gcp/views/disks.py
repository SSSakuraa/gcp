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
    if func_name == "disk_insert":
        return gcp_disk_insert(param)

    if func_name == "disk_insert_batch":
        return gcp_disk_insert_batch(param)

    if func_name == "disk_list":
        return gcp_disk_list(param)

    if func_name == "disk_info":
        return gcp_disk_info(param)

    if func_name == "disk_info_batch":
        return gcp_disk_info_batch(param)


def gcp_disk_insert(param):
    import rstr
    disk_list = gcp_disk_func("disk_list", param)
    while True:
        name = rstr.xeger('[a-z](?:[-a-z0-9]{0,61}[a-z0-9])?')
        if name not in disk_list:
            break
    disk_body = {
        "name": name,
        "sizeGb": param['sizeGb'],
        "storageType": param['storageType']
    }
    myrequest = param['service'].disks().insert(
        project=param['project'], zone=param['zone'], body=disk_body)
    myresponse = myrequest.execute()
    res = {
        'id': myresponse['targetId'],
        'status': myresponse['status'],
        'name': myresponse['targetLink'].split('/disks/')[1]
    }
    return res


# insert disks batch
# [{'size': 100, 'type': 'HDD', 'iops': 100},
#  {'size': 100, 'type': 'HDD', 'iops': 100},
#  {'size': 100, 'type': 'HDD', 'iops': 100},
#  {'size': 100, 'type': 'HDD', 'iops': 100}
#  ]
# return disk name and error info
def gcp_disk_insert_batch(param):
    ebs=param['ebs']
    instance_disk = []
    index = 0
    for disk in ebs:
        disk_param = {
            'project': param['project'],
            'zone': param['zone'],
            'service': param['service'],
            'sizeGb': disk['size'],
            'storageType': disk['type']
        }
        try:
            index = index + 1
            disk_name = gcp_disk_func(
                "disk_insert", disk_param)['name']
            instance_disk.append({'disk_name': disk_name})
        except errors.HttpError as e:
            instance_disk.append({
                'error': json.loads(e.content)['error']['message'],
                'disk_index': index})
    return instance_disk




# get disk name for all disks
def gcp_disk_list(param):
    myrequest = param['service'].disks().list(
        project=param['project'], zone=param['zone'])
    disk_list = []
    while myrequest is not None:
        myresponse = myrequest.execute()
        for disk in myresponse['items']:
            # TODO: Change code below to process each `disk` resource:
            disk_list.append(disk['name'])

        myrequest = param['service'].disks().list_next(
            previous_request=myrequest, previous_response=myresponse)
    return disk_list


def gcp_disk_info(param):
    myrequest = param['service'].disks().get(
        project=param['project'], zone=param['zone'], disk=param['disk_name'])
    myresponse = myrequest.execute()
    res = {
        'id': myresponse['id'],
        'create_time': myresponse['creationTimestamp'],
        'size': myresponse['sizeGb'],
        'status': myresponse['status'],
        'type': myresponse['type'].split('/diskTypes/')[1]
    }
    return res


def gcp_disk_info_batch(param):
    instance_disk=param['instance_disk_name']
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