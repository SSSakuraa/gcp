import urllib2
import re
from pprint import pprint

class Fee(object):
    def __init__(self):
        self.city_dict=self.get_city()
        self.instance_price=self.instance_price()
        self.disk_price=self.disk_price()
    

    def get_city(self):
        user_agent=''
        headers={}
        request=urllib2.Request("https://cloud.google.com/compute/pricing")
        response=urllib2.urlopen(request)
        html=response.read()

        select_list = re.split('\n',re.findall(re.compile(r'<md-select([\s\S]*?)</md-select>'),html)[0])
        city_dict = {}
        for option in select_list:
            if 'value' in option:
                citys=re.split("\">|\"|<",option)
                city_dict[citys[2]]=citys[3]
        return city_dict

    def instance_price(self):
        user_agent=''
        headers={}
        request=urllib2.Request("https://cloud.google.com/compute/pricing")
        response=urllib2.urlopen(request)
        html=response.read()

        city_dict=self.city_dict
        tr_list=re.findall(re.compile(r'<tr>([\s\S]*?)</tr>'),html) 
        price_dict={}
        machine_info={}
        for tr in tr_list:
            if "monthly" in tr: 
                td_list=re.split('</td>',tr)
                machine_type=re.findall(re.compile(r'[a-z][0-9]+-[a-z]+[-0-9]*'),td_list[0])[0]
                price_dict[machine_type]=machine_info
                if 'default' in td_list[1]:
                    cpu=re.split('default=\"|\">',td_list[1])[1]
                else:
                    cpu=re.split('<td>',td_list[1])[1]
                machine_info['cpu']=cpu
                if 'default' in td_list[2]:
                    memory=re.split('default=\"|\">',td_list[2])[1]
                else:
                    memory=re.split('<td>',td_list[1])[1]
                machine_info['memory']=memory
                prices=re.split('\n',td_list[3].strip())
                price_info={}
                machine_info['price']=price_info
                for price in prices:
                    if 'monthly' in price:
                        price=re.split('-monthly=\"|\"',price.strip())
                        price_info[city_dict[price[0]]]=price[1][1:]

            if len(price_dict)==21:
                break
    #        pprint(price_dict)
        return price_dict

    def disk_price(self):
        user_agent=''
        headers={}
        request=urllib2.Request("https://cloud.google.com/compute/pricing")
        response=urllib2.urlopen(request)
        html=response.read()

        city_dict=self.city_dict
        tr_list=re.findall(re.compile(r'<tr>([\s\S]*?)</tr>'),html)
        price_dict={}
        for tr in tr_list:
            if "Standard provisioned space" in tr: 
                td_list=re.split('\n',tr)
                for price in td_list:
                    if '-monthly=' in price:
                        price=re.split('-monthly=\'|\'',price.strip())
                        price_dict[city_dict[price[0]]]=price[1][1:]

#                pprint(price_dict)
        return price_dict
