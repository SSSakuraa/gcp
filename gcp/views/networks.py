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
        auth=Auth() 
        service=auth.get_service(request)
        myrequest = service.networks().list(project=auth.project)
        networks = []
        while myrequest is not None:
            myresponse = myrequest.execute()
        
            for network in myresponse['items']:
                # TODO: Change code below to process each `address` resource:
                #            pprint(address)
                networks.append(network)
                pprint(network)
            myrequest = service.networks().list_next(previous_request=myrequest, previous_response=myresponse)
        return jsonify(items = networks,total=len(networks))
    except errors.HttpError as e:
        msg=json.loads(e.content)
        return jsonify(msg=msg),msg["error"]["code"]


@networks.route('/vpcs',methods=['POST'])
def insert():
    from flask import request
    data=json.loads(request.get_data())
    
    network_body = {
                # TODO: Add desired entries to the request body.
                'name':data['name']
                }

    myrequest = service.networks().insert(project=project, body=network_body)
    myresponse = myrequest.execute()

    # TODO: Change code below to process the `response` dict:
    pprint(myresponse)
    return jsonify(myresponse)
