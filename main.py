## Imports
from flask import Flask, render_template, request, redirect, flash, abort
import pymysql
from dynaconf import Dynaconf
import flask_login
## Imports


## Application
app = Flask(__name__)


## Settings
conf = Dynaconf(
    settings_file = ["settings.toml"]
)


## Secret Key
app.secret_key = conf.secret_key


## Login Manager
login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view=("/login")


## User Class
class User:
    is_authenticated = True
    is_anonymous = False
    is_active = True

    def __init__(self, user_id, username, password, zipcode):
        self.id = user_id
        self.username = username
        self.password = password
        self.zip = zipcode

    def get_id(self):
        return str(self.id)


## Connect to Database
def conn_db():
    conn = pymysql.connect(
        host = "db.steamcenter.tech",
        database = "cheap_carts",
        user = "hjinan",
        password = conf.password,
        autocommit = True,
        cursorclass = pymysql.cursors.DictCursor
    )

    return conn


## User Session
@login_manager.user_loader
def load_user(user_id):
    conn = conn_db()
    
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Users` WHERE `id` = {user_id};")

    result = cursor.fetchone()

    ## Close Connections
    cursor.close()
    conn.close()

    if result is not None:
        return User(result["id"], result["username"], result["password"], result["zipcode"])