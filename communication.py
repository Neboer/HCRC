import requests
from config import minecraft_server_address


def check_user_from_server(username, password) -> bool:
    response = requests.get(f'{minecraft_server_address}/user/login', {
        'username': username,
        'password': password
    })
    body = response.text
    return body == "success"


def add_user_to_server(username, password):
    # invitor不发往后端，是作为奖励传达的。.
    response = requests.post(f'{minecraft_server_address}/user/register', params={
        'username': username,
        'password': password
    })
    return response.text == "success"


def change_user_password_from_server(username, original_password, new_password):
    response = requests.post(f'{minecraft_server_address}/user/password/change', params={
        'username': username,
        'old_password': original_password,
        'new_password': new_password
    })
    return response.text == "success"


def del_user_from_server(username):
    response = requests.post(f'{minecraft_server_address}/user/delete', params={
        'username': username
    })
    return response.text == "success"


def get_user_list_from_server():
    return requests.get(f'{minecraft_server_address}/user/all').json()


def give_kit(username, kit_name):
    response = requests.post(f'{minecraft_server_address}/kit/give', params={
        'username': username,
        'name': kit_name
    })
    return response.text == 'success'
