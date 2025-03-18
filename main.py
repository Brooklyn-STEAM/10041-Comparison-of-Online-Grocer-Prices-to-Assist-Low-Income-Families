#<--- Imports --->#
from flask import Flask, render_template, request, redirect, flash, abort
import pymysql
from dynaconf import Dynaconf
import flask_login
from scraper import scrape
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

    def __init__(self, user_id, username, zipcode):
        self.id = user_id
        self.username = username
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
        return User(result["id"], result["username"], result["zipcode"])
    

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
        username = request.form["username"].strip().replace(" ", "")
        zipcode = request.form["zipcode"].strip().replace(" ", "")
        password = request.form["password"].strip().replace(" ", "")
        confpass = request.form["confirm_password"].strip().replace(" ", "")

        conn = conn_db()

        cursor = conn.cursor()

        if len(username) >20:
            flash("Username must be 20 characters or less.")

        else:
            if len(password) < 8:
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
@app.route("/login", methods=["POST", "GET"])
def login():
    if flask_login.current_user.is_authenticated:
        return redirect("/products")
    
    if request.method == "POST":
        username = request.form["userVer"].strip().replace(" ", "")
        password = request.form["passVer"].strip().replace(" ", "")

        conn = conn_db()

        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM `Users` WHERE `username` = '{username}';")

        result = cursor.fetchone()

        ##Close Connections
        cursor.close()
        conn.close()

        if result is None:
            flash("Your username and/or password is incorrect.")
        
        elif password != result["password"]:
            flash("Your username and/or password is incorrect.")

        else:
            user = User(result["id"], result["username"], result["zipcode"])

            flask_login.login_user(user)

            return redirect("/products")
        
    return render_template("login.html.jinja")


## Popular Products Page
@app.route("/products")
def popular_products():
    conn = conn_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Products`;  ")

    results = cursor.fetchall()

    return render_template("popular_products.html.jinja", products=results)


## Comparison Page
@app.route("/compare/<products_id>")
def comparison(products_id):
    conn = conn_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Products` WHERE `id` = {products_id};  ")

    result = cursor.fetchone()

    cursor.execute(f"SELECT * FROM `CompanyList`; ")

    comp_results = cursor.fetchall()

    return render_template("comparison.html.jinja", products=result, comp_products = comp_results)


## Leftovers Page
@app.route("/leftovers")
@flask_login.login_required
def leftovers():
    conn = conn_db()
    cursor = conn.cursor()

    user_id = flask_login.current_user.id

    cursor.execute(f"SELECT * FROM `Cart` WHERE `user_id` = {user_id};")

    results = cursor.fetchall()

    return render_template("saved_products.html.jinja", products=results)

## Add Items to Leftovers
@app.route("/leftovers/save")
@flask_login.login_required
def save ():
    conn = conn_db()
    cursor = conn.cursor()

    user_id = flask_login.current_user.id

    
    return redirect("/leftovers")

## Guide Page
@app.route("/guide")
def guide():
   return render_template("guide.html.jinja")

## Account Page
@app.route("/settings")
@flask_login.login_required
def account():
    return render_template("account.html.jinja")


## Log Out
@app.route("/logout")
def logout():
    flask_login.logout_user()
    return redirect("/")