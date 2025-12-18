import requests
import json
from os.path import isfile
import time
from tqdm import tqdm
import sys


odota_url = 'https://api.opendota.com/api/'
stratz_url = 'https://stratz.com/api/v1/'


# def get_match(id: int) -> dict:
#     url = MATCH_URL + f"/{id}"
#     try:
#         return requests.get(
#             url=url,
#             headers=head
#         ).json()
#     except Exception as e:
#         print(e)




def get_match(m_id):
    local_cache = 'data\\match_files\\'
    # check local cache first before calling api
    file_path = local_cache + str(m_id) + '.json'
    if isfile(file_path):
        with open(file_path) as fp:
            return json.load(fp)

    call_url = odota_url + '/matches/' + str(m_id)
    response = requests.get(call_url)
    if not response.ok:
        print(response.status_code, response.reason)
        sys.exit()
    result = response.json()
    time.sleep(1)  # rate limit safety
    with open(file_path, 'w') as fp:
        json.dump(result, fp, indent=4)
    return result



def pro_list(n=100):
    match_list = []
    params = {'less_than_match_id': 100000000000}

    list_file = 'data\\pro_matches.txt'
    if isfile(list_file):
        with open(list_file) as fp:
            match_list = fp.read().splitlines()
        params['less_than_match_id'] = min(match_list)


    while len(match_list) < n:
        response = requests.get(odota_url + 'proMatches', params=params)
        result = response.json()
        match_batch = [str(elt['match_id']) for elt in result]
        params['less_than_match_id'] = min(match_batch)
        match_list += match_batch
        time.sleep(1)  # rate limit safety

    with open(list_file, 'w') as fp:
        fp.write('\n'.join(match_list))

    return match_list[:n]

def pub_list(n=100):
    match_list = []
    params = {
                'less_than_match_id': 100000000000,
                'min_rank': 10
            }

    list_file = 'data\\pub_matches.txt'
    if isfile(list_file):
        with open(list_file) as fp:
            match_list = fp.read().splitlines()
        params['less_than_match_id'] = min(match_list)

    while len(match_list) < n:
        # response = requests.get(odota_url + 'publicMatches', params=params)
        response = requests.get(odota_url + 'parsedMatches', params=params)
        result = response.json()
        match_batch = [str(elt['match_id']) for elt in result]
        params['less_than_match_id'] = min(match_batch)
        match_list += match_batch
        time.sleep(1)  # rate limit safety

    with open(list_file, 'w') as fp:
        fp.write('\n'.join(match_list))

    return match_list[:n]

def main():
    # pros = pro_list(1000)
    # for pro_match in tqdm(pros):
    #     match = get_match(pro_match)

    pubs = pub_list(1000)
    for pub_match in tqdm(pubs):
        match = get_match(pub_match)





if __name__ == '__main__':
    main()

