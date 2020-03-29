import random
import socket
import string
import struct
from datetime import datetime

from communication import give_kit
from config import award
from player import Player


def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]


def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))


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


# 珏对的核心代码，
def create_new_user(cursor, db, username, password, invitor, invitor_code, phone_number, force=False):
    current_timestamp = int(datetime.now().timestamp())
    invitation_code_list = generate_invitation_code_list(cursor)
    cursor.execute(
        "INSERT INTO new_players (player_name, password, register_timestamp, invitor_username, phone_number) VALUES (?,?,?,?,?)",
        (username, password, current_timestamp, invitor, phone_number))
    cursor.executemany("INSERT INTO invite_codes (code, generate_user_name) VALUES (?,?)",
                       [(code, username) for code in invitation_code_list])
    if not force:
        cursor.execute("UPDATE invite_codes SET used_user_name=? WHERE code=?", (username, invitor_code))
    db.commit()


def get_user_from_local(cursor, username):
    cursor.execute(
        "SELECT player_id, player_name, password, register_timestamp, invitor_username FROM new_players WHERE player_name=?",
        (username,))
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


#
def record_ip_sms_time_to_local_db(cursor, db, ip_addr_string):
    # 为了节省空间，存入数据库的ip地址为整数。
    ip_addr_int = ip2int(ip_addr_string)
    current_time_int = int(datetime.now().timestamp())
    cursor.execute("SELECT * from ip_sms_record WHERE ip_addr=?", (ip_addr_int,))
    search_result = cursor.fetchone()
    if search_result:
        cursor.execute("UPDATE ip_sms_record SET last_msg_time=?, req_count=req_count+1 WHERE ip_addr=?",
                       (current_time_int, ip_addr_int,))
    else:
        cursor.execute("INSERT INTO ip_sms_record (ip_addr, last_msg_time, req_count) VALUES (?,?,?)",
                       (ip_addr_int, current_time_int, 0))
    db.commit()


def get_ip_sms_time_from_db(cursor, ip_addr_string):
    # 如果成功，返回一个datetime对象，如果ip从未请求过，则返回空
    ip_addr_int = ip2int(ip_addr_string)
    cursor.execute("SELECT last_msg_time FROM ip_sms_record WHERE ip_addr=?", (ip_addr_int,))
    result = cursor.fetchone()
    if result:
        return datetime.fromtimestamp(result[0])
    else:
        return False


def give_kit_to_invitor(cursor, username):
    cursor.execute('select count(*) from new_players where invitor_username = ?', (username,))
    result = cursor.fetchone()
    award_name = award[int(result[0])]
    give_kit(username, award_name)


def is_phone_exist(cursor, phone):
    cursor.execute('select * from new_players where phone_number = ?', (phone,))
    result = cursor.fetchone()
    return result is not None
