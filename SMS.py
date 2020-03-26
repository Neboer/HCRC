import json
import random

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from config import *

client = AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')


def get_code() -> str:
    code = ''.join([
        str(random.randint(0, 9))
        for _ in range(6)
    ])

    return code


def send_code(phone: str, code: str):
    request = CommonRequest()
    request.set_accept_format('json')
    request.set_domain('dysmsapi.aliyuncs.com')
    request.set_method('POST')
    request.set_protocol_type('https')
    request.set_version('2017-05-25')
    request.set_action_name('SendSms')

    request.add_query_param('RegionId', "cn-hangzhou")
    request.add_query_param('PhoneNumbers', phone)
    request.add_query_param('SignName', "日冕游戏平台")
    request.add_query_param('TemplateCode', "SMS_186619468")
    request.add_query_param('TemplateParam', json.dumps({'code': code}))

    client.do_action_with_exception(request)
