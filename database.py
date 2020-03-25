import sqlite3, random, string
from datetime import datetime
from player import Player


def _query_one_invitation_code(cursor, code_str, index):
    code_index = str(index)
    cursor.execute(f"SELECT username FROM players WHERE code{code_index}=?", (code_str,))
    username_con = cursor.fetchone()
    if username_con:
        cursor.execute(f"SELECT code{code_index}_used FROM players WHERE username=?", (username_con[0],))
        invitation_con = cursor.fetchone()
        return username_con[0], invitation_con[0]
    else:
        return None, None


# 检测用户输入的邀请码是否存在、是否已被使用，返回有此邀请码的用户和用此邀请码注册的人，最后还会有一个这是邀请者的第几个激活码。
def query_invitation_code(cursor, code_str):
    for index in (1, 2, 3):
        username, invitation_tacker = _query_one_invitation_code(cursor, code_str, index)
        if username:
            return username, invitation_tacker, index
    return None, None, None


def _random_string(stringLength=6):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(stringLength))


# 不做任何简化，拒绝！
def generate_triple_invitation_code(cursor):
    invitation_code_list = []
    random_string_1 = _random_string()
    while query_invitation_code(cursor, random_string_1)[0]:
        random_string_1 = _random_string()
    invitation_code_list.append(random_string_1)
    random_string_2 = _random_string()
    while query_invitation_code(cursor, random_string_2)[0] or random_string_2 in invitation_code_list:
        random_string_2 = _random_string()
    invitation_code_list.append(random_string_2)
    random_string_3 = _random_string()
    while query_invitation_code(cursor, random_string_3)[0] or random_string_3 in invitation_code_list:
        random_string_3 = _random_string()
    invitation_code_list.append(random_string_3)
    return invitation_code_list


def create_new_user(cursor, db, username, password, invitor, invitor_code_index):
    current_timestamp = int(datetime.now().timestamp())
    invitation_code_list = tuple(generate_triple_invitation_code(cursor))
    cursor.execute(
        "INSERT INTO players (username, password, register_timestamp, invitor, code1, code2,\
         code3) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (username, password, current_timestamp, invitor,) + invitation_code_list)
    if invitor != "Admin":
        cursor.execute(
            f"UPDATE players SET code{invitor_code_index}_used=? WHERE username=?", (username, invitor,))
    db.commit()


def get_user(cursor, username):
    cursor.execute("SELECT * FROM players WHERE username=?", (username,))
    user_tuple = cursor.fetchone()
    if user_tuple:
        return Player(*user_tuple[:5], user_tuple[5:8], user_tuple[8:12])
    else:
        return None


def change_password_from_local_db(cursor, db, username, new_password):
    cursor.execute("UPDATE players SET password=? WHERE username=?", (new_password, username,))
    db.commit()
    return
