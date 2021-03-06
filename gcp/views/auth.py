
import json

from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
from flask import request

from aes import AESCipher
from regions import *


class Auth(object):
    def __init__(self):
        self.project = ''
        self.region = ''
#        self.zone=''

    def aes_decrypt(self, client_id, client_secret, refresh_token):
        key = "sakura"
        inst = AESCipher(key)
        client_id = inst.decrypt(client_id)
        client_secret = inst.decrypt(client_secret)
        refresh_token = inst.decrypt(refresh_token)
        return client_id, client_secret, refresh_token

    # return google service for GET method
    def get_service(self, request):
        data = request.args.to_dict()
        (client_id, client_secret, refresh_token) = self.aes_decrypt(
            data['client_id'], data['client_secret'], data['refresh_token'])
        if 'project_id' in data.keys():
            self.project = data['project_id']
        if 'region_id' in data.keys():
            self.region = data['region_id']
        elif 'region_name' in data.keys():
            self.region = Region().get_region_id(data['region_name'])
#        if request.args.get('zone')!=None and self.region != '':
#            self.zone=self.region+'-'+request.args.get('zone')

        credentials = GoogleCredentials(access_token=None,
                                        client_id=client_id,
                                        client_secret=client_secret,
                                        refresh_token=refresh_token,
                                        token_expiry=None,
                                        token_uri='https://www.googleapis.com/oauth2/v4/token',
                                        user_agent='Python client library')

        service = discovery.build('compute', 'beta', credentials=credentials)
        return service

    # return google servcie for POST method
    def post_service(self, request):
        data = json.loads(request.get_data())
        (client_id, client_secret, refresh_token) = self.aes_decrypt(
            data['client_id'], data['client_secret'], data['refresh_token'])
        if 'project_id' in data.keys():
            self.project = data['project_id']
        if 'region_id' in data.keys():
            self.region = data['region_id']
        elif 'region_name' in data.keys():
            self.region = Region().get_region_id(data['region_name'])
#        if data.has_key('zone') and self.region != '':
#            self.zone=self.region+'-'+data['zone']

        credentials = GoogleCredentials(access_token=None,
                                        client_id=client_id,
                                        client_secret=client_secret,
                                        refresh_token=refresh_token,
                                        token_expiry=None,
                                        token_uri='https://www.googleapis.com/oauth2/v4/token',
                                        user_agent='Python client library')

        service = discovery.build('compute', 'beta', credentials=credentials)
        return service
