import requests


def check_user_from_server(username, password):
    if username == 'test' and password == 'good':
        return True


def add_user_to_server(username, password, invitor):
    # invitor不发往后端，是作为奖励传达的。.
    return True


def change_user_password_from_server(username, original_password, new_password):
    return True


def del_user_from_server(username):
    pass


def get_user_list_from_server():
    return []
