import requests

from config import minecraft_server_host, minecraft_server_path

header = {
    'Host': minecraft_server_host,
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36',
    'Accept': '*/*',
}

url = f"https://{minecraft_server_host}{minecraft_server_path}"


def check_user_from_server(username, password) -> bool:
    response = requests.get(f'{url}/user/login', params={
        'username': username,
        'password': password
    }, headers=header)
    body = response.text
    return body == "success"


def add_user_to_server(username, password):
    # invitor不发往后端，是作为奖励传达的。.
    response = requests.post(f'{url}/user/register', params={
        'username': username,
        'password': password
    }, headers=header)
    return response.text == "success"


def change_user_password_from_server(username, original_password, new_password):
    response = requests.post(f'{url}/user/password/change', params={
        'username': username,
        'old_password': original_password,
        'new_password': new_password
    }, headers=header)
    return response.text == "success"


def del_user_from_server(username):
    response = requests.post(f'{url}/user/delete', params={
        'username': username
    }, headers=header)
    return response.text == "success"


def get_user_list_from_server():
    return [i['username'] for i in requests.get(f'{url}/user/all').json()]

def give_kit(username, kit_name):
    response = requests.post(f'{url}/kit/give', params={
        'username': username,
        'name': kit_name
    }, headers=header)
    return response.text == 'success'
