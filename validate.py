import re
from enum import Enum


class ValidateError(Enum):
    bad_request = 1
    bad_string = 2
    bad_cookie = 3
    captcha_error = 4

    def toStr(self):
        maper = {ValidateError.bad_request: "请求错误", ValidateError.bad_string: "数据格式错误",
                 ValidateError.bad_cookie: "请求未带身份信息", ValidateError.captcha_error: "验证码错误"}
        return maper[self]


def validate_password_string(password_string):
    return bool(re.match(r"[1-9a-i]{6,16}", password_string))


def pre_validate_invite_code(invite_code):
    return bool(re.match(r"[1-9a-zA-Z]{6}", invite_code))


def validate_exist_username(username):
    return len(username) > 0


def pre_validate_request(operation, request, session):
    pre = {'username': "", 'original_password': "", "password": "", "invite_code": ""}
    # pre对象有什么意义呢？pre用来在用户的输入犯小错误的情况下，再次生成的页面里涵盖之前用户输入过的信息，起到一个方便用户的作用。
    dialect = {
        "登录": ('username', 'password', 'captcha'),
        "注册": ('username', 'password', 'invite_code', 'captcha'),
        "修改密码": ('original_password', 'password', 'captcha')
    }
    form = request.form
    for item in dialect[operation]:
        if item not in form:
            return ValidateError.bad_request, pre
        else:
            if item == 'username':
                if validate_exist_username(form['username']):
                    pre['username'] = form['username']
                else:
                    return ValidateError.bad_string, pre
            if item == 'password' or item == 'original_password':
                if validate_password_string(form[item]):
                    pre[item] = form[item]
                else:
                    return ValidateError.bad_string, pre
            if item == 'invite_code':
                if pre_validate_invite_code(form['invite_code']):
                    pre['invite_code'] = form['invite_code']
                else:
                    return ValidateError.bad_string, pre
    if 'username' in session and pre['username'] == "":
        pre['username'] = session['username']
    if 'captcha' not in session:
        return ValidateError.bad_cookie, pre
    if operation == '修改密码' and 'username' not in session:
        return ValidateError.bad_cookie, pre
    if session['captcha'] != form['captcha']:
        return ValidateError.captcha_error, pre
    return None, pre
