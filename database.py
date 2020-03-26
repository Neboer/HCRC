import sqlite3, random, string
from datetime import datetime
from player import Player


# def _query_one_invitation_code(cursor, code_str, index):
#     code_index = str(index)
#     cursor.execute(f"SELECT username FROM players WHERE code{code_index}=?", (code_str,))
#     username_con = cursor.fetchone()
#     if username_con:
#         cursor.execute(f"SELECT code{code_index}_used FROM players WHERE username=?", (username_con[0],))
#         invitation_con = cursor.fetchone()
#         return username_con[0], invitation_con[0]
#     else:
#         return None, None


# 检测用户输入的邀请码是否存在、是否已被使用，返回有此邀请码的用户和用此邀请码注册的人。
def query_invitation_code(cursor, code_str):
    cursor.execute("SELECT generate_user_name, used_user_name FROM invite_codes WHERE code=?", (code_str,))
    invite_code_record = cursor.fetchone()
    if invite_code_record:
        return invite_code_record  # 有可能是None哦~！
    else:
        return None, None


def _random_string(stringLength=6):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase + string.ascii_uppercase + string.digits
    return ''.join(random.choice(letters) for i in range(stringLength))


def generate_invitation_code_list(cursor, count=3):
    invitation_code_list = []
    for times in range(count):
        rand_string = _random_string()
        while query_invitation_code(cursor, rand_string)[0] or rand_string in invitation_code_list:
            rand_string = _random_string()
        invitation_code_list.append(rand_string)
    return invitation_code_list


# def _create_new_user_bk(cursor, db, username, password, invitor, invitor_code_index):
#     current_timestamp = int(datetime.now().timestamp())
#     invitation_code_list = tuple(generate_invitation_code_list(cursor))
#     cursor.execute(
#         "INSERT INTO players (username, password, register_timestamp, invitor, code1, code2,\
#          code3) VALUES (?, ?, ?, ?, ?, ?, ?)",
#         (username, password, current_timestamp, invitor,) + invitation_code_list)
#     if invitor != "Admin":
#         cursor.execute(
#             f"UPDATE players SET code{invitor_code_index}_used=? WHERE username=?", (username, invitor,))
#     db.commit()


def create_new_user(cursor, db, username, password, invitor, invitor_code, force=False):
    current_timestamp = int(datetime.now().timestamp())
    invitation_code_list = generate_invitation_code_list(cursor)
    cursor.execute("INSERT INTO new_players (player_name, password, register_timestamp, invitor_username) VALUES (?,?,?,?)",
                   (username, password, current_timestamp, invitor))
    cursor.executemany("INSERT INTO invite_codes (code, generate_user_name) VALUES (?,?)",
                       [(code, username) for code in invitation_code_list])
    if not force:
        cursor.execute("UPDATE invite_codes SET used_user_name=? WHERE code=?", (username, invitor_code))
    db.commit()


def get_user_from_local(cursor, username):
    cursor.execute("SELECT * FROM new_players WHERE player_name=?", (username,))
    user_tuple = cursor.fetchone()
    if user_tuple:
        cursor.execute("SELECT code, used_user_name FROM invite_codes WHERE generate_user_name=?", (username,))
        user_code_list = cursor.fetchmany(size=3)
        return Player(*user_tuple, [record[0] for record in user_code_list],
                      [record[1] for record in user_code_list])
    else:
        return None


def change_password_from_local_db(cursor, db, username, new_password):
    cursor.execute("UPDATE new_players SET password=? WHERE player_name=?", (new_password, username,))
    db.commit()
    return
