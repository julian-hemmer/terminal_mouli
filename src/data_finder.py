import requests
import json
import requests.cookies
import requests
import time
import os

import token_updater

base_url = "https://api.epitest.eu/me"

def make_request(token, url):
    req_header = {
        'Content-Type': 'applications/json',
        'Authorization': f'Bearer {token}'
    }
    return requests.get(f"{url}", headers=req_header)

def fetch_data(token, url):
    while True:
        if token == "":
            token = token_updater.get_newtoken()
            continue
        #print(f"Used Token '{token[:10]}' to fetch data at '{url}'.")
        request = make_request(token, url)
        if request.status_code == 200:
            break
        #print(f"Waiting 2s before retrying.")
        time.sleep(2)
        token = token_updater.get_newtoken()
        
    token_updater.save_token(token)
    return json.loads(request.text)

def ecofetch_data(token, url, force = False):
    mouli_data = {}
    url_path = url.replace(base_url, "").replace("/", "")
    #print(f"Getting current mouli data '{url_path}'")
    
    if os.path.isfile(f"data/{url_path}.mouli") and not force:
        #print(f"Getting current mouli data '{url}'")
        with open(f'data/{url_path}.mouli', "r") as file:
            mouli_data = json.load(file)
            if time.time() - mouli_data["last_update"] > 30:
                mouli_data = {}
    
    if len(mouli_data) == 0 or force:
        #print("Fetching new mouli data")
        mouli_data["data"] = fetch_data(token, url)
        mouli_data["last_update"] = time.time()

        os.makedirs(os.path.dirname(f'data/{url_path}.mouli'), exist_ok=True)
        with open(f'data/{url_path}.mouli', "w") as file:
            json.dump(mouli_data, file)

    return mouli_data
