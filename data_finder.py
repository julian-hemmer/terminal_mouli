
import requests
import json
import requests.cookies
import requests
import time
import os.path

import token_updater

def save_token(token):
    with open("token_file", "w") as file:
        file.write(token)

def load_token():
    if not os.path.isfile("token_file"):
        token = reload_token()
        save_token(token)
    else:
        with open("token_file", "r") as file:
            token = file.read()
    return token

def reload_token():
    return token_updater.get_token()

def make_request(token, url):
    req_header = {
        'Content-Type': 'applications/json',
        'Authorization': f'Bearer {token}'
    }
    return requests.get(f"{url}", headers=req_header)

def fetch_data(token, url):
    while True:
        print(f"Used Token '{token[:10]}' to fetch data at '{url}'.")
        request = make_request(token, url)
        if request.status_code == 200:
            break
        print(f"Waiting 3s before retrying.")
        time.sleep(3)
        token = reload_token()
        save_token(token)

    return json.loads(request.text)
