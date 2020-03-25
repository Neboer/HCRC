from flask import Flask, request, render_template, make_response, session, g, redirect
from communication import *
from database import *
from validate import validate_new_username, validate_password_string, validate_invite_code, validate_exist_username
import sqlite3
from base64 import b64encode
from os import urandom

app = Flask(__name__)

# with open("config.json", "r", encoding="utf8") as config_file:
#     config = json.load(config_file)
# cursor, db = connect()

DATABASE = 'HCRC.sqlite'
app.secret_key = urandom(26)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# hello.html：用户没有登录时看到的界面。
@app.route('/')
def hello_page():
    return render_template('Hello.html')


@app.route('/login', methods=['GET'])
def login_page():
    db = get_db()
    cursor = db.cursor()
    if 'username' in session:
        user = get_user(cursor, session.get('username'))
        return render_template('User.html', info=user)
    else:
        return render_template('Login.html', operation="登录")


@app.route('/login', methods=['POST'])
def login():
    db = get_db()
    cursor = db.cursor()
    username = request.form['username']
    password = request.form['password']
    if validate_exist_username(username) and validate_password_string(password):
        # 先在本地查找一下用户，如果找到了，就是血赚。
        user_info = get_user(cursor, username)
        if user_info:
            if password == user_info.password:
                session['username'] = username
                session.modified = True
                return render_template('User.html', info=user_info, user_information='登录成功')
            else:
                return render_template('Login.html', operation="登录", err='用户名或密码错误')
        else:
            user_info = check_user_from_server(username, password)
            # 服务器上有这个用户，但是本地数据库里没有，说明数据库内容不全，需要写。
            if user_info:
                create_new_user(cursor, db, username, password, "Admin", 0)
        if user_info:
            # 登陆成功，立刻set cookie
            session['username'] = username
            session.modified = True
            return render_template('User.html', user_information='登录成功', info=user_info)
        else:
            return render_template('Login.html', operation="登录", err='用户名或密码错误')
    else:
        return render_template('Login.html', operation="登录", err='用户名或密码错误')


@app.route('/register', methods=['GET'])
def register_page():
    resp = make_response(render_template('Login.html', operation="注册"))
    return resp


@app.route('/register', methods=['POST'])
def register():
    db = get_db()
    cursor = db.cursor()
    username = request.form['username']
    password = request.form['password']
    invitation_code = request.form['invite_code']
    name_check = validate_new_username(username, cursor)
    if name_check == -1:
        error_message = "该用户已经被注册"
    elif name_check == 1:
        error_message = "用户名不能为空"
    else:
        if not validate_password_string(password):
            error_message = "密码必须为1-9a-i的6-16位字符串"
        else:
            if not validate_invite_code(invitation_code):
                error_message = "邀请码不存在"
            else:
                invitor, usage, index = query_invitation_code(cursor, invitation_code)
                if invitor and not usage:
                    add_result = add_user_to_server(username, password, invitor)
                    if add_result:
                        create_new_user(cursor, db, username, password, invitor, index)
                        player_already_added = get_user(cursor, username)
                        return render_template('User.html', info=player_already_added, user_information='注册成功')
                    else:
                        error_message = "服务端错误"
                elif invitor and usage:
                    error_message = "该邀请码已经被注册"
                else:
                    error_message = "邀请码不存在"
    return render_template('Login.html', operation="注册", err=error_message)


@app.route('/change_password', methods=['GET'])
def change_password_page():
    username = session.get('username')
    resp = make_response(render_template('Login.html', operation="修改密码", user_change_password=username))
    return resp


@app.route('/change_password', methods=['POST'])
def change_password():
    db = get_db()
    cursor = db.cursor()
    username = session.get('username')
    if not username:
        return render_template('Login.html', operation="登录")
    else:
        original_password = request.form['original_password']
        new_password = request.form['password']
        if validate_password_string(new_password) and validate_password_string(original_password):
            real_user = get_user(cursor, username)
            if not real_user:
                # 其实这个不太可能了。但是……万一呢？
                result = change_user_password_from_server(username, original_password, new_password)
                if result:
                    create_new_user(cursor, db, username, new_password, "Admin", 0)
                    user = get_user(cursor, username)
                    return render_template('User.html', user_information="修改密码成功", info=user)
                else:
                    return render_template('Login.html', operation="修改密码", user_change_password=username, err="密码错误")
            else:
                if original_password == real_user.password:
                    if change_user_password_from_server(username, original_password, new_password):
                        change_password_from_local_db(cursor, db, username, new_password)
                        user = get_user(cursor, username)
                        return render_template('User.html', user_information="修改密码成功", info=user)
                    else:
                        return render_template('Login.html', operation="修改密码", user_change_password=username,
                                               err="服务器错误")
                else:
                    return render_template('Login.html', operation="修改密码", user_change_password=username, err="密码错误")
        else:
            return render_template('Login.html', operation="修改密码", user_change_password=username, err="密码格式错误")


@app.route('/logout', methods=['GET'])
def log_out():
    session.pop('username')
    return redirect('/')
# @app.route('/captcha', methods=['GET'])
# def captcha():
#     image = ImageCaptcha()
#     data = image.generate('1234')
