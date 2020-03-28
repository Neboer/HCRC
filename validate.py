import re
from enum import Enum
from config import captcha_letters


class ValidateError(Enum):
    bad_request = 1
    bad_string = 2
    bad_cookie = 3
    captcha_error = 4

    def toStr(self):
        maper = {ValidateError.bad_request: "1请求错误", ValidateError.bad_string: "2数据格式错误",
                 ValidateError.bad_cookie: "3请求未带身份信息", ValidateError.captcha_error: "4验证码错误"}
        return maper[self]


def pre_validate_request(operation, request, session):
    pre = {'username': "", 'original_password': "", "password": "", "invite_code": "", "phone": ""}
    # pre对象有什么意义呢？pre用来在用户的输入犯小错误的情况下，再次生成的页面里涵盖之前用户输入过的信息，起到一个方便用户的作用。
    dialect = {
        "登录": ('username', 'password', 'captcha'),
        "注册": ('username', 'password', 'invite_code', 'captcha', 'phone', 'code'),
        "修改密码": ('original_password', 'password', 'captcha')
    }
    form = request.form
    pattern = {
        'username': r'.+',
        'password': r"^[1-9a-i]{6,16}$",
        'original_password': r"^[1-9a-i]{6,16}$",
        'invite_code': r'^[1-9a-zA-Z]{6}$',
        'captcha': f'^[{captcha_letters}]{{4}}$',
        'phone': r'^1([34578])\d{9}$',
        'code': r'^[0-9]{6}$'
    }
    error = None
    for item in dialect[operation]:
        if item not in form:
            error = ValidateError.bad_request
        else:
            if re.match(pattern[item], form[item]):
                pre[item] = form[item]
            else:
                error = ValidateError.bad_string
                return error, pre
    if 'username' in session and pre['username'] == "":
        pre['username'] = session['username']
    if 'captcha' not in session:
        error = ValidateError.bad_cookie
    elif operation == '修改密码' and 'username' not in session:
        error = ValidateError.bad_cookie
    elif session['captcha'] != form['captcha']:
        error = ValidateError.captcha_error
    return error, pre


# 对sms请求进行预先的检验。检验这个请求是否传递正确的captcha，检验请求是否传递正确的手机号码
def pre_validate_sms_request(request, session):
    phone = request.args.get("phone")
    captcha = request.args.get("captcha")
    if not phone or not captcha:
        return ValidateError.bad_request
    if 'captcha' not in session:
        return ValidateError.bad_cookie
    if session.get('captcha') != captcha:
        return ValidateError.captcha_error
    if not re.match(r'^1([34578])\d{9}$', phone):
        return ValidateError.bad_string
    return
