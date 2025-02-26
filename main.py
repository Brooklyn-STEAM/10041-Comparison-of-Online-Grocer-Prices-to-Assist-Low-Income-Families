#<--- Imports --->#
from flask import Flask, render_template, request, redirect, flash, abort
import pymysql
from dynaconf import Dynaconf
import flask_login
#<--- Imports --->#


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
        user = conf.username,
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
    

#<--- Routes --->#
## Homepage
@app.route("/")
def index():
    return render_template("homepage.html.jinja")


## Sign Up Page
@app.route("/register", methods=["POST", "GET"])
def signup():
    if flask_login.current_user.is_authenticated:
        return redirect("/products")
    
    if request.method =="POST":
        username = request.form["username"]
        zipcode = request.form["zipcode"]
        password = request.form["password"]
        confpass = request.form["confirm_password"]

        conn = conn_db()

        cursor = conn.cursor()

        if len(username.strip()) >20:
            flash("Username must be 20 characters or less.")

        else:
            if len(password.strip()) < 8:
                flash("Password must be 8 characters or longer.")
            
            else:
                if password != confpass:
                    flash("Passwords do not match.")
                
                else:
                    try:
                        cursor.execute(f"""
                            INSERT INTO `Users`
                                (`username`, `password`, `zipcode`)
                            VALUES
                                ('{username}', '{password}', '{zipcode}');
                        """)
                    
                    except pymysql.err.IntegrityError:
                        flash("Username is already in use.")
                    
                    else:
                        return redirect("/login")
                    
                    finally:
                        ##Close Connections
                        cursor.close()
                        conn.close()

    return render_template("signup.html.jinja")


## Log In Page
@app.route("/login")
def login():
    return render_template("login.html.jinja")


## Popular Products Page
@app.route("/products")
def popular_products():
    return render_template("popular_products.html.jinja")


## Comparison Page
@app.route("/compare")
def comparison():
    return render_template("comparison.html.jinja")


## Leftovers Page
@app.route("/leftovers")
@flask_login.login_required
def leftovers():
    return render_template("saved_products.html.jinja")


## Account Page
@app.route("/settings")
@flask_login.login_required
def account():
    return render_template("account.html.jinja")