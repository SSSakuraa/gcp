import urllib2
import re
from pprint import pprint


def get_fee():
    fee=Fee()
    pprint("==================")
    pprint(fee.city_dict)
    pprint("==================")
    return fee




class Fee(object):
    def __init__(self):
        self.city_dict = self.get_city()
        self.instance_price = self.instance_price()
        self.disk_price = self.disk_price()

    # get city names from google website
    def get_city(self):
        request = urllib2.Request("https://cloud.google.com/compute/pricing")
        response = urllib2.urlopen(request)
        html = response.read()

        select_list = re.split('\n', re.findall(re.compile(
            r'<md-select([\s\S]*?)</md-select>'), html)[0])
        city_dict = {}
        for option in select_list:
            if 'value' in option:
                citys = re.split("\">|\"|<", option)
                city_dict[citys[2]] = citys[3]
        return city_dict

    # get instance price from google website
    def instance_price(self):
        request = urllib2.Request("https://cloud.google.com/compute/pricing")
        response = urllib2.urlopen(request)
        html = response.read()

        tr_list = re.findall(re.compile(r'<tr>([\s\S]*?)</tr>'), html)
        price_dict = {}
        machine_info = {}
        for tr in tr_list:
            if "monthly" in tr:
                td_list = re.split('</td>', tr)
                machine_type = re.findall(re.compile(
                    r'[a-z][0-9]+-[a-z]+[-0-9]*'), td_list[0])[0]
                price_dict[machine_type] = machine_info
                if 'default' in td_list[1]:
                    cpu = re.split('default=\"|\">', td_list[1])[1]
                else:
                    cpu = re.split('<td>', td_list[1])[1]
                machine_info['cpu'] = cpu
                if 'default' in td_list[2]:
                    memory = re.split('default=\"|\">', td_list[2])[1]
                else:
                    memory = re.split('<td>', td_list[1])[1]
                machine_info['memory'] = memory
                prices = re.split('\n', td_list[3].strip())
                price_info = {}
                machine_info['price'] = price_info
                for price in prices:
                    if 'monthly' in price:
                        price = re.split('-monthly=\"|\"', price.strip())
                        price_info[self.city_dict[price[0]]
                                   ] = float(price[1][1:])

            if len(price_dict) == 21:
                break
    #        pprint(price_dict)
        return price_dict

    # get disk price from google website
    def disk_price(self):
        request = urllib2.Request("https://cloud.google.com/compute/pricing")
        response = urllib2.urlopen(request)
        html = response.read()

        city_dict = self.city_dict
        tr_list = re.findall(re.compile(r'<tr>([\s\S]*?)</tr>'), html)
        price_dict = {}
        for tr in tr_list:
            if "Standard provisioned space" in tr:
                standard_price = {}
                price_dict['HDD'] = standard_price
                td_list = re.split('\n', tr)
                for price in td_list:
                    if '-monthly=' in price:
                        price = re.split('-monthly=\'|\'', price.strip())
                        standard_price[city_dict[price[0]]
                                       ] = float(price[1][1:])
            elif "<td>SSD provisioned space</td>" in tr:
                ssd_price = {}
                price_dict['SSD'] = ssd_price
                td_list = re.split('\n', tr)
                for price in td_list:
                    if '-monthly=' in price:
                        price = re.split('-monthly=\'|\'', price.strip())
                        ssd_price[city_dict[price[0]]] = float(price[1][1:])
            elif "<td>Snapshot storage</td>" in tr:
                snapshot_price = {}
                price_dict['snapshot'] = ssd_price
                td_list = re.split('\n', tr)
                for price in td_list:
                    if '-monthly=' in price:
                        price = re.split('-monthly=\'|\'', price.strip())
                        snapshot_price[city_dict[price[0]]
                                       ] = float(price[1][1:])
#                pprint(price_dict)
        return price_dict
