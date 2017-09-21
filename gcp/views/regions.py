
regions={
        'Iowa':'us-central1',
        'Oregon':'us-west1',
        'South Carolina':'us-east1',
        'N. Virginia':'us-east4',
        'S\u00e3o Paulo':'southamerica-east1',
        'London':'europe-west2',
        'Belgium':'europe-west1',
        'Frankfurt':'europe-west3',
        'Singapore':'asia-southeast1',
        'Taiwan':'asia-west1',
        'Tokyo':'asia-northeast1',
        'Sydney':'australia-southeast1'
        }

def region_match(region_id,region_name):
    if regions.has_key(region_name)==False:
        return False
    if regions[region_name]==region_id:
        return True
    else:
        return False



def get_region_id(region_name):
    if regions.has_key(region_name):
        return regions[region_name]
    else:
        return ""



def get_region_name(region_id):
    for k,v in regions.items():
        if v==region_id:
            return k
    return ""
