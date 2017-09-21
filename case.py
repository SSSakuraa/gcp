#!/usr/bin/python
from aes import AESCipher
import json
import urllib
import commands
import re

# Credential params
credentials={
        "client_id": "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com",
        "client_secret": "d-FL95Q19q7MQmFpd7hHD0Ty",
        "refresh_token": "1/SpPoXuKbSJhph1KfT_SmyzDdXeM2EHs-A7bPNdLsk_o",
        "type": "authorized_user"
        }

# encrypt for google credential params
def aes_encrypt():
    key="sakura"
    inst=AESCipher(key)
    body=credentials
#    print json.dumps(body,indent=4)
    body['client_id']=inst.encrypt(credentials['client_id'])
    body['client_secret']=inst.encrypt(credentials['client_secret'])
    body['refresh_token']=inst.encrypt(credentials['refresh_token'])
#    print json.dumps(body,indent=4)


if __name__=="__main__":
    ip="35.197.44.232"
    aes_encrypt()
    string=raw_input("input the command index:")
    while string!="quit":
        # not defined in doc.
        if string=="get/vpcs/list":
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
#                    'project_id':'dsafdsfa'
                    }
            url_data=urllib.urlencode(form_data)

            url="http://"+ip+":5000/vpcs/list?"+url_data
            command = "curl '%s' -i 2>/dev/null" % url
            print command
            res=commands.getoutput(command) 
            print(res)

        # get instance information.
        elif re.match(r"get/servers/(.*)",string)!=None:
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
#                    'region_id':'us-east1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'zone':'a',
                    }
            instance_id=string[12:]
#            instance_id="instance-1"
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_id+"?"+url_data
            command = "curl '%s' -i  2>/dev/null" % url
            print command
            res=commands.getoutput(command) 
            print(res)

        # create instance
        # TODO
        elif string == 'post/servers':
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-17551',  # project_code in doc
                    'vpc_cidr':'', # not used in gcp networks with subnetworks
                    'vpc_id':'',
                    'zone':'us-west1-a',
                    # it is no use while vpc_id is valid
                    'is_common':0,  # 0 means vpc for project, 1 means global vpc   
                    'subnet_cidr':'',
                    'cost_center':'', # not used in gcp
                    'region_name':'Oregon',
                    'region_id':'',
                    'name':'name',
                    }
#            instance_id="instance-1"
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers"
            command = "curl '%s' -i -d '%s' -X POST  2>/dev/null" % (url, json.dumps(form_data))
            print command
            res=commands.getoutput(command) 
            print(res)

        # instance operations
        elif re.match(r"post/servers/(.*)/on",string)!=None:
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
#                    'region_id':'us-est1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'action':'server_on',
                    'zone':'a',
                    'dry_run':True
                    }
            instance_id=string[13:len(string)-3]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_id
            command = "curl '%s' -i -X POST -d '%s' 2>/dev/null" % (url,json.dumps(form_data))
            print command
            res=commands.getoutput(command) 
            print(res)

        # instance operations
        elif re.match(r"post/servers/(.*)/off",string)!=None:
#        elif string=="get":
#            string="post/servers/papa/off"
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
#                    'region_id':'us-est1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'action':'server_off',
                    'zone':'a',
                    'dry_run':True
                    }
            instance_id=string[13:len(string)-4]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_id
            command = "curl '%s' -i -X POST -d '%s' 2>/dev/null" % (url,json.dumps(form_data))
            print command
            res=commands.getoutput(command) 
            print(res)

        # instance operations
        elif re.match(r"post/servers/(.*)/delete",string)!=None:
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
#                    'region_id':'us-est1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'action':'server_delete',
                    'zone':'a',
                    'dry_run':True
                    }
            instance_id=string[13:len(string)-7]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_id
            command = "curl '%s' -i -X POST -d '%s' 2>/dev/null" % (url,json.dumps(form_data))
            print command
            res=commands.getoutput(command) 
            print(res)
        # instance operations
        elif re.match(r"post/servers/(.*)/oft",string)!=None:
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
#                    'region_id':'us-est1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'action':'server_oft',
                    'zone':'a',
                    'dry_run':True
                    }
            instance_id=string[13:len(string)-4]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_id
            command = "curl '%s' -i -X POST -d '%s' 2>/dev/null" % (url,json.dumps(form_data))
            print command
            res=commands.getoutput(command) 
            print(res)
        
        # instance operations
        elif re.match(r"post/servers/(.*)/modify",string)!=None:
#        elif string == "get":
#            string='post/servers/papa/modify'
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
#                    'region_id':'us-est1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'action':'server_modify',
                    'zone':'a',
                    'dry_run':True,
                    'dst_inst_type':'n1-standardddddd-2'
                    }
            instance_id=string[13:len(string)-7]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_id
            command = "curl '%s' -i -X POST -d '%s' 2>/dev/null" % (url,json.dumps(form_data))
            print command
            res=commands.getoutput(command) 
            print(res)
        elif re.match(r"post/servers/(.*)/reboot",string)!=None:

#        elif string == "get":
#            string='post/servers/papa/modify'
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
#                    'region_id':'us-est1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'action':'server_reboot',
                    'zone':'a',
                    'dry_run':True
                    }
            instance_id=string[13:len(string)-7]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_id
            command = "curl '%s' -i -X POST -d '%s' 2>/dev/null" % (url,json.dumps(form_data))
            print command
            res=commands.getoutput(command)
            print(res)
        elif string == "post/servers/batch":
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
#                    'region_id':'us-est1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'action':'server_modify',
                    'zone':'a',
                    'dry_run':True,
                    'dst_inst_type':'n1-standard-8',
                    'instances':["instance-1","instance-2","dsfsdaf","papa"]
                    }
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/batch"
            command = "curl '%s' -i -X POST -d '%s'  2>/dev/null" % (url,json.dumps(form_data))
            print command
            res=commands.getoutput(command)
            print(res)
        # create instance
        elif string == "get/servers/batch":
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
#                    'region_id':'us-est1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'zone':'a',
                    'instances':['instance-1','instance-2','dsfsdaf','papa']
                    }
            url_data=urllib.urlencode(form_data)
            url='http://'+ip+':5000/servers/batch?'+url_data
            command = "curl '%s' -i -X GET 2>/dev/null" % url
            print command
            res=commands.getoutput(command)
            print(res)
        elif string=="fee":
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
#                    'region_id':'us-east1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'instance_type':'n1-standard-8',
                    'ebs':[{'size':'100','type':'standard','iops':100},
                        {'size':'100','type':'standard','iops':100},
                        {'size':'100','type':'standard','iops':100},
                        {'size':'100','type':'standard','iops':100}

                    ],
                    'os':'os',
                    'quantity':100
                    }
#            instance_id="instance-1"
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/fee?"+url_data
            command = "curl '%s' -i  2>/dev/null" % url
            print command
            res=commands.getoutput(command) 
            print(res)

        else:
            print("error")
            
        string=raw_input("input the command index:")
