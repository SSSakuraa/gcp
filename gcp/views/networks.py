from flask import Blueprint
from pprint import pprint
from flask import jsonify
from flask import request
from auth import Auth
from googleapiclient import errors
import json


networks=Blueprint('networks',__name__)

@networks.route('/vpcs/list',methods=['GET'])
def list():
    try:
        auth = Auth()
        service = auth.get_service(request)
        param = {
            'project': auth.project,
            'service': service,
        }
        res=gcp_network_func("vpc_list",param)
        return jsonify(res)
    except errors.HttpError as e:
        msg=json.loads(e.content)
        return jsonify(msg=msg),msg["error"]["code"]


# @networks.route('/vpcs',methods=['POST'])
# def insert():
#     from flask import request
#     data=json.loads(request.get_data())
    
#     network_body = {
#                 # TODO: Add desired entries to the request body.
#                 'name':data['name']
#                 }

#     myrequest = service.networks().insert(project=project, body=network_body)
#     myresponse = myrequest.execute()

#     # TODO: Change code below to process the `response` dict:
#     pprint(myresponse)
#     return jsonify(myresponse)


# function interface for google API
def gcp_network_func(func_name,param):
    service = param['service']
    project = param['project']
    
    if func_name == "vpc_list":
        myrequest = service.networks().list(project=project)
        network_list = []
        while myrequest is not None:
            myresponse = myrequest.execute()
        
            for network in myresponse['items']:
                network_list.append(network)
                pprint(network)
            myrequest = service.networks().list_next(previous_request=myrequest, previous_response=myresponse)
        return network_list