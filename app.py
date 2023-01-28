from flask import Flask, request, flash, render_template, redirect, url_for, send_from_directory
from flask_login import UserMixin, LoginManager, login_required, logout_user, login_user, current_user
from markupsafe import escape
import yaml

app = Flask(__name__,
            # static_url_path='',
            static_folder='./site',
            template_folder='./templates')

# Default Configuration
DEBUG_FLAG = False
LISTEN_PORT = 8030
LOGIN_ENABLED = False

# decorate the existing decorator login_required
def login_required_(f):
    global LOGIN_ENABLED
    if LOGIN_ENABLED:
        return login_required(f)
    else:
        return f

app.secret_key = '123456'


# emulated database
class UserService:
    yaml_path = './users.yaml'
    with open(yaml_path, 'r') as f:
        users = yaml.safe_load(f)

    @classmethod
    def query_user_by_name(cls, username):
        for user in cls.users:
            if username == user['username']:
                return user

    @classmethod
    def query_user_by_id(cls, user_id):
        for user in cls.users:
            if user_id == user['id']:
                return user


login_manager = LoginManager()

# params
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
login_manager.login_message = 'Access denied.'

login_manager.init_app(app)  # init login manager


# user class
class User(UserMixin):
    pass


# load user callback
@login_manager.user_loader
def user_loader(user_id: str):
    """
    [NOTE] user_id is str type
    :param user_id:
    :return:
    """
    if UserService.query_user_by_id(int(user_id)) is not None:
        curr_user = User()
        curr_user.id = user_id
        return curr_user


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    # username = request.form.get('username', None)

    # get json data
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    print(f"username={username}, password={password}")

    if not username:
        # flash('username is required!')
        response = {
            "status": "fail",
            "message": "username is required!"
        }
        # return render_template('login.html')
        return response
    user = UserService.query_user_by_name(username)

    if user is not None and password == user['password']:
        curr_user = User()
        curr_user.id = user['id']

        print(f"try to login user: {curr_user.get_id()}")
        # 通过Flask-Login的login_user方法登录用户
        login_user(curr_user)

        # 登录成功后重定向
        # next_url = request.args.get('next')
        # print(f"next_url={next_url}")
        # next_url = '/'
        # return redirect(next_url or url_for('index'))
        # return send_from_directory(app.static_folder, 'index.html')
        # print(f"url_for('index')={url_for('index')}")

        response = {
            "status": "success",
            "message": "login success",
            "redirect": url_for('index')
        }
        # return redirect(url_for('index'))
        return response
    else:
        # flash('Wrong username or password!')
        # return render_template('login.html')
        response = {
            "status": "fail",
            "message": "Wrong username or password!"
        }
        return response


# logout
@app.route('/logout')
@login_required_
def logout():
    # 通过Flask-Login的logout_user方法登出用户
    logout_user()
    return 'Logged out successfully!'


# index
@app.route('/')
@login_required_
def index():
    return send_from_directory(app.static_folder, 'index.html')


# access protected resource
@app.route('/<path:url>')
@login_required_
def serve_static(url):
    # use markupsafe to escape the url
    url = escape(url)

    # if url ends with a slash, append index.html
    if url.endswith('/'):
        url += 'index.html'

    # mine type check
    if url.endswith('.js'):
        return send_from_directory(app.static_folder, url, mimetype='text/javascript')
    elif url.endswith('.css'):
        return send_from_directory(app.static_folder, url, mimetype='text/css')
    elif url.endswith('.html'):
        return send_from_directory(app.static_folder, url, mimetype='text/html')
    elif url.endswith('.png'):
        return send_from_directory(app.static_folder, url, mimetype='image/png')
    elif url.endswith('.jpg'):
        return send_from_directory(app.static_folder, url, mimetype='image/jpeg')
    elif url.endswith('.gif'):
        return send_from_directory(app.static_folder, url, mimetype='image/gif')
    elif url.endswith('.svg'):
        return send_from_directory(app.static_folder, url, mimetype='image/svg+xml')
    elif url.endswith('.ico'):
        return send_from_directory(app.static_folder, url, mimetype='image/x-icon')
    elif url.endswith('.json'):
        return send_from_directory(app.static_folder, url, mimetype='application/json')
    elif url.endswith('.ttf'):
        return send_from_directory(app.static_folder, url, mimetype='font/ttf')
    return send_from_directory(app.static_folder, url)


if __name__ == '__main__':
    app.run(debug=DEBUG_FLAG, host='0.0.0.0', port=LISTEN_PORT)