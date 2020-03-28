from datetime import datetime, timedelta
from uuid import uuid4

from SMS import get_code, send_code
from config import SMS_active_seconds

# 短信发送功能的控制模块。
# 这个全局变量中存储的信息如下：(uuid4,'13000000001','a14s',datetime())，第一个是每个记录独特的id。
SMS = []


def SMS_go(phone):
    code = get_code()
    send_code(phone, code)
    SMS.append((uuid4(), phone, code, datetime.now()))
    return


def _delete_by_id(id):
    for index, i in enumerate(SMS):
        if i[0] == id:
            del SMS[index]


def SMS_checkout(phone, code):
    result = False
    now = datetime.now()
    for h_uid, h_phone, h_code, h_time in reversed(SMS.copy()):
        # 如果记录已经超时，那么按照超时处理。
        if now - h_time > timedelta(seconds=SMS_active_seconds):
            _delete_by_id(h_uid)
            continue
        if h_phone == phone and h_code == code:
            # 完全成功，删除原来的元素。
            _delete_by_id(h_uid)
            result = True
    return result
