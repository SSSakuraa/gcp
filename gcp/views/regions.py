
regions={
        'us-central1':'Iowa',
        'us-west1':'Oregon',
        'us-east1':'South Carolina',
        'us-east4':'N. Virginia',
        'southamerica-east1':'Sao Paulo',
        'europe-west2':'London',
        'europe-west1':'Belgium',
        'europe-west3':'Frankfurt',
        'asia-southeast1':'Singapore',
        'asia-west1':'Taiwan',
        'asia-northeast1':'Tokyo',
        'australia-southeast1':'Sydney'
        }


def region_match(region_id,region_name):
    if regions.has_key(region_id)==False:
        return False
    if regions[region_id]==region_name:
        return True
    else:
        return False



def get_region_name(region_id):
    if regions.has_key(region_id):
        return regions[region_id]
    else:
        return ""



def get_region_id(region_name):
    for k,v in regions.items():
        if v==region_name:
            return k
    return ""
