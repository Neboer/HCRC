import re
from database import get_user
from communication import get_user_list_from_server


def validate_new_username(username_string, cursor):
    if len(username_string) > 0:
        if get_user(cursor, username_string) or username_string in get_user_list_from_server():
            return -1  # -1 代表用户已经被注册了。
        else:
            return 0  # 0 用户没有被注册
    else:
        return 1  # 1 字符串不合法。


def validate_password_string(password_string):
    return bool(re.match(r"[1-9a-i]{6,16}", password_string))


def validate_invite_code(invite_code):
    return bool(re.match(r"[1-9a-zA-Z]{6}", invite_code))


def validate_exist_username(username):
    return len(username) > 0
