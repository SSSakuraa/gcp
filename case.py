#!/usr/bin/python
from aes import AESCipher
import json
import urllib
import commands
import re
from pprint import pprint
# Credential params
credentials = {
    "client_id": "764086051850-6qr4p6gpi6hn506pt8ejuq83di341hur.apps.googleusercontent.com",
    "client_secret": "d-FL95Q19q7MQmFpd7hHD0Ty",
    "refresh_token": "1/SpPoXuKbSJhph1KfT_SmyzDdXeM2EHs-A7bPNdLsk_o",
    "type": "authorized_user"
}

# encrypt for google credential params
def aes_encrypt():
    key = "sakura"
    inst = AESCipher(key)
    body = credentials
#    print json.dumps(body,indent=4)
    body['client_id'] = inst.encrypt(credentials['client_id'])
    body['client_secret'] = inst.encrypt(credentials['client_secret'])
    body['refresh_token'] = inst.encrypt(credentials['refresh_token'])
#    print json.dumps(body,indent=4)


if __name__=="__main__":
    ip = "35.197.44.232"
    aes_encrypt()
    string = raw_input("input the command index:")
    while string != "quit":
        # not defined in doc.
        if string == "get/vpcs/list":
            form_data = {
                'client_id': credentials['client_id'],
                'client_secret': credentials['client_secret'],
                'refresh_token': credentials['refresh_token'],
                'project_id': 'saintern-175510',
                # 'project_id':'dsafdsfa'
            }
            url_data = urllib.urlencode(form_data)

            url = "http://" + ip + ":5000/vpcs/list?" + url_data
            command = "curl '%s' -i" % url
            pprint(command)
            res = commands.getoutput(command)
            print(res)

        # get instance information.
        elif re.match(r"get/servers/(.*)",string)!=None:
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
                    'region_id':'us-west1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'zone':'a',
                    }
            instance_name=string[12:]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_name+"?"+url_data
            command = "curl '%s' -i" % url
            pprint(command)
            res=commands.getoutput(command) 
            print(res)

        # create instance
        # TODO
        elif string == 'post/servers1':
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-17551',
                    'vpc_id':'155979844223948781', # only vpc_id can identify the vpc.
                    'vpc_cidr':'10.240.0.0/16', # vpc with subnets has no vpc_cidr
                    'zone':'a',
                    # it is no use while vpc_id is valid
                    'is_common':0,  # 0 means vpc for project, 1 means global vpc   
                    'subnet_cidr':'',
                    'cost_center':'', # not used in gcp
                    'region_name':'Oregon',
                    'region_id':'us-west1',
                    'name':'name',
                    'instance_type': 'n1-standard-2',
                    'ebs':[{'size':100,'type':'standard','iops':100},
                        {'size':100,'type':'standard','iops':100},
                        {'size':100,'type':'standard','iops':100},
                        {'size':100,'type':'standard','iops':100}

                    ],
                    'image':'projects/debian-cloud/global/images/debian-9-stretch-v20170829',
                    'server_type':'gameaudit', # miao???
                    'sg_name':'game-sg', # not used in gcp
                    'sg_rules':[], # not used in gcp
                    'iam_role':'', # not used in gcp
                    'eip_enable':1, # 0:disable; 1:enable
                    'userdata':'', # miao???
                    'dry_run':False,
                    'os':'debian-9-stretch',
                    'quantity':2,
                    'tags':{'key':'value'},
                    'private_ips':[]
                    }

#            instance_id="instance-1"
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers"
            command = "curl '%s' -i -d '%s' -X POST " % (url, json.dumps(form_data))
            pprint(command)
            res=commands.getoutput(command) 
            print(res)
        

        elif string == 'post/servers2':
            form_data={
                'client_id':credentials['client_id'],
                'client_secret':credentials['client_secret'],
                'refresh_token':credentials['refresh_token'],
                'project_id':'saintern-17551',
                'region_name':'Oregon',
                'region_id':'us-west1',
                'zone':'a',
                'vpc_cidr':'10.240.0.0/16', # vpc without subnets can have cidr
                'vpc_id':'155979844223948781',
                # it is no use while vpc_id is valid
                'is_common':0,  # 0:vpc for project; 1:global vpc. gcp has no global vpc. 
                'subnet_cidr':'',
                'cost_center':'', # not used in gcp
                'instance_type': 'n1-standard-2',
                'ebs_encrypt':0, # not used in gcp


                }
#            instance_id="instance-1"
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers"
            command = "curl '%s' -i -d '%s' -X POST " % (url, json.dumps(form_data))
            pprint(command)
            res=commands.getoutput(command) 
            print(res)

        # instance operations
        elif re.match(r"post/servers/(.*)/on",string)!=None:
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
                    'region_id':'us-west1',
                    'region_name':'Oregon',
#                    'project_id':'dsafdsfa'
                    'action':'server_on',
                    'zone':'a',
                    'dry_run':True
                    }
            instance_name=string[13:len(string)-3]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_name
            command = "curl '%s' -i -X POST -d '%s' " % (url,json.dumps(form_data))
            pprint(command)
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
                    'region_name':'Oregon',
                    'region_id':'us-west1',
                    'action':'server_off',
                    'zone':'a',
                    'dry_run':False
                    }
            instance_name=string[13:len(string)-4]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_name
            command = "curl '%s' -i -X POST -d '%s' " % (url,json.dumps(form_data))
            pprint(command)
            res=commands.getoutput(command) 
            print(res)

        # instance operations
        elif re.match(r"post/servers/(.*)/delete",string)!=None:
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
                    'region_id':'us-west1',
                    'region_name':'Oregon',
                    'action':'server_delete',
                    'zone':'a',
                    'dry_run':True
                    }
            instance_name=string[13:len(string)-7]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_name
            command = "curl '%s' -i -X POST -d '%s' " % (url,json.dumps(form_data))
            pprint(command)
            res=commands.getoutput(command) 
            print(res)

        # instance operations
        elif re.match(r"post/servers/(.*)/oft",string)!=None:
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
                    'region_id':'us-west1',
                    'region_name':'Oregon',
                    'action':'server_oft',
                    'zone':'a',
                    'dry_run':True
                    }
            instance_name=string[13:len(string)-4]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_name
            command = "curl '%s' -i -X POST -d '%s'" % (url,json.dumps(form_data))
            pprint(command)
            res=commands.getoutput(command) 
            print(res)
        
        # instance operations
        elif re.match(r"post/servers/(.*)/modify",string)!=None:
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
                    'region_id':'us-west1',
                    'region_name':'Oregon',
                    'action':'server_modify',
                    'zone':'a',
                    'dry_run':True,
                    'dst_inst_type':'n1-standard-2'
                    }
            instance_name=string[13:len(string)-7]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_name
            command = "curl '%s' -i -X POST -d '%s' " % (url,json.dumps(form_data))
            pprint(command)
            res=commands.getoutput(command) 
            print(res)

        # instance operations
        elif re.match(r"post/servers/(.*)/reboot",string)!=None:
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
                    'region_id':'us-west1',
                    'region_name':'Oregon',
                    'action':'server_reboot',
                    'zone':'a',
                    'dry_run':True
                    }
            instance_name=string[13:len(string)-7]
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/servers/"+instance_name
            command = "curl '%s' -i -X POST -d '%s' " % (url,json.dumps(form_data))
            pprint(command)
            res=commands.getoutput(command)
            print(res)

        # instance batch operations
        elif string == "post/server/batch":
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
                    'region_id':'us-west1',
                    'region_name':'Oregon',
                    'action':'server_modify',
                    'zone':'a',
                    'dry_run':True,
                    'dst_inst_type':'n1-standard-8',
                    'instances':["instance-1","instance-2","dsfsdaf","papa"]
                    }
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/server/batch"
            command = "curl '%s' -i -X POST -d '%s' " % (url,json.dumps(form_data))
            pprint(command)
            res=commands.getoutput(command)
            print(res)

        # instance batch info
        elif string == "get/server/batch":
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
                    'region_id':'us-west1',
                    'region_name':'Oregon',
                    'zone':'a',
                    'instances':['instance-1','instance-2','dsfsdaf','papa']
                    }
            url_data=urllib.urlencode(form_data)
            url='http://'+ip+':5000/server/batch?'+url_data
            command = "curl '%s' -i -X GET " % url
            pprint(command)
            res=commands.getoutput(command)
            print(res)
        
        # instance fee
        elif string=="fee":
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
                    'region_id':'us-west1',
                    'region_name':'Oregon',
                    'instance_type':'n1-standard-8',
                    'ebs':[{'size':100,'type':'standard','iops':100},
                        {'size':100,'type':'standard','iops':100},
                        {'size':100,'type':'standard','iops':100},
                        {'size':100,'type':'standard','iops':100}

                    ],
                    'os':'os',
                    'quantity':100
                    }
#            instance_id="instance-1"
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/fee?"+url_data
            command = "curl '%s' -i  " % url
            pprint(command)
            res=commands.getoutput(command) 
            print(res)
        
        elif string=="state":
            form_data={
                    'client_id':credentials['client_id'],
                    'client_secret':credentials['client_secret'],
                    'refresh_token':credentials['refresh_token'],
                    'project_id':'saintern-175510',
                    'region_id':'us-west1',
                    'region_name':'Oregon',
                    'instance':'instance-3',
                    'zone':'a'
                    }
            url_data=urllib.urlencode(form_data)
            url="http://"+ip+":5000/state?"+url_data
            command = "curl '%s' -i  " % url
            pprint(command)
            res=commands.getoutput(command) 
            print(res)
        else:
            print("error")
            
        string=raw_input("input the command index:")
