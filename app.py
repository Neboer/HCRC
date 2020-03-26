from flask import Flask, request, render_template, make_response, session, g, redirect
from communication import *
from database import *
from validate import pre_validate_request, ValidateError
import sqlite3
from captcha_generate import captcha_response
from os import urandom

app = Flask(__name__)

# with open("config.json", "r", encoding="utf8") as config_file:
#     config = json.load(config_file)
# cursor, db = connect()

DATABASE = 'HCRC.sqlite'
app.secret_key = urandom(26)
default_pre = {'username': "", 'original_password': "", "password": "", "invite_code": ""}


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
    if 'username' in session:
        return redirect('/login')
    return render_template('Hello.html')


@app.route('/login', methods=['GET'])
def login_page():
    db = get_db()
    cursor = db.cursor()
    if 'username' in session:
        user = get_user_from_local(cursor, session.get('username'))
        return render_template('User.html', info=user)
    else:
        return render_template('Login.html', operation="登录", pre=default_pre)


@app.route('/login', methods=['POST'])
def login():
    validate_result, pre = pre_validate_request("登录", request, session)
    if validate_result:
        return render_template('Login.html', operation="登录", err=validate_result.toStr(), pre=pre)
    db = get_db()
    cursor = db.cursor()
    username = request.form['username']
    password = request.form['password']
    # 先在本地查找一下用户，如果找到了，就是血赚。
    user_info = get_user_from_local(cursor, username)
    if user_info:
        if password == user_info.password:
            session['username'] = username
            session.modified = True
            return render_template('User.html', info=user_info, user_information='登录成功')
        else:
            return render_template('Login.html', operation="登录", err='用户名或密码错误', pre=pre)
    else:
        outer_login_success = check_user_from_server(username, password)
        if outer_login_success:
            # 服务器上有这个用户，但是本地数据库里没有，说明数据库内容不全，需要写。
            create_new_user(cursor, db, username, password, "Admin", 0, force=True)
            user_info = get_user_from_local(cursor, username)
            return render_template('User.html', user_information='登录成功', info=user_info)
        else:
            return render_template('Login.html', operation="登录", err='用户名或密码错误', pre=pre)


@app.route('/register', methods=['GET'])
def register_page():
    return render_template('Login.html', operation="注册", pre=default_pre)


@app.route('/register', methods=['POST'])
def register():
    validate_result, pre = pre_validate_request("注册", request, session)
    if validate_result:
        return render_template('Login.html', operation="注册", err=validate_result.toStr(), pre=pre)
    db = get_db()
    cursor = db.cursor()
    username = request.form['username']
    password = request.form['password']
    invitation_code = request.form['invite_code']
    name_check_already_exists = bool(get_user_from_local(cursor, username)) or username in get_user_list_from_server()
    if name_check_already_exists:
        return render_template('Login.html', operation="注册", err="该用户名已经被注册", pre=pre)
    invitor, usage = query_invitation_code(cursor, invitation_code)
    if invitor and not usage:
        add_result = add_user_to_server(username, password)
        if add_result:
            create_new_user(cursor, db, username, password, invitor, invitation_code)
            player_already_added = get_user_from_local(cursor, username)
            session['username'] = username
            return render_template('User.html', info=player_already_added, user_information='注册成功')
        else:
            return render_template('Login.html', operation="注册", err="服务器错误", pre=pre)
    if invitor and usage:
        return render_template('Login.html', operation="注册", err="该邀请码已被使用", pre=pre)
    return render_template('Login.html', operation="注册", err="邀请码不存在", pre=pre)


@app.route('/change_password', methods=['GET'])
def change_password_page():
    if 'username' not in session:
        return redirect('/')
    else:
        username = session.get('username')
        new_pre = default_pre.copy()
        new_pre['username'] = username
        return render_template('Login.html', operation="修改密码", user_change_password=username, pre=new_pre)


@app.route('/change_password', methods=['POST'])
def change_password():
    validate_result, pre = pre_validate_request("修改密码", request, session)
    if validate_result:
        return render_template('Login.html', operation="修改密码", err=validate_result.toStr(), pre=pre)
    db = get_db()
    cursor = db.cursor()
    username = session.get('username')
    original_password = request.form['original_password']
    new_password = request.form['password']
    real_user = get_user_from_local(cursor, username)
    if not real_user:
        # 其实这个不太可能了。但是……万一呢？
        result = change_user_password_from_server(username, original_password, new_password)
        if result:
            create_new_user(cursor, db, username, new_password, "Admin", 0, force=True)
            user = get_user_from_local(cursor, username)
            return render_template('User.html', user_information="修改密码成功", info=user)
        else:
            return render_template('Login.html', operation="修改密码", user_change_password=username, err="密码错误", pre=pre)
    if original_password == real_user.password:
        if change_user_password_from_server(username, original_password, new_password):
            change_password_from_local_db(cursor, db, username, new_password)
            user = get_user_from_local(cursor, username)
            return render_template('User.html', user_information="修改密码成功", info=user)
    return render_template('Login.html', operation="修改密码", user_change_password=username, err="密码错误", pre=pre)


@app.route('/logout', methods=['GET'])
def log_out():
    if 'username' in session:
        session.pop('username')
    return redirect('/')


@app.route('/captcha/<rand>', methods=['GET'])
def captcha(rand):
    res, ans = captcha_response()
    session['captcha'] = ans
    return res
