import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_qrcode import QRcode
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, pokemon


def gen_key():
    return (random.choice(pokemon)).lower() + "-" + str(random.randint(100, 999))


# Configure application
app = Flask(__name__)
# QRApp
QRcode(app)
# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///clips.db")


# If hosting on PythonAnyWhere
# db = SQL("sqlite:////home/username/sitename/clips.db")
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html", pokemon=pokemon)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        user_id = session["user_id"]
        title = request.form.get("title")
        key = request.form.get("key")
        lang = request.form.get("lang")
        pw = request.form.get("pw")
        if pw == "":
            pw_req = 0
        else:
            pw_req = 1
        pw = generate_password_hash(request.form.get("pw"))
        code = request.form.get("code")
        if title == "":
            flash("Please enter a title", "yellow")
            return redirect("/create")
        if key == "":
            flash("Please enter a key", "yellow")
            return redirect("/create")
        if code == "":
            flash("Please enter the code", "yellow")
            return redirect("/create")
        try:
            db.execute(
                "INSERT INTO history (user_id ,title, key, lang ,code, pw, pw_req) VALUES (? ,? ,? , ?, ?, ?, ?)",
                user_id,
                title,
                key,
                lang,
                code,
                pw,
                pw_req,
            )
        except:
            flash("Choose a different key.", "red")
            return redirect("/create")
        flash("Saved Successfully! Your key is " + key, "green")
        return redirect("/dashboard")
    else:
        hash = gen_key()
        return render_template("create.html", hash=hash)


@app.route("/dashboard")
@login_required
def dashboard():
    user_id = session["user_id"]
    query = db.execute(
        "SELECT title,key,lang,SUBSTR(code, 1, 100) AS code,time,pw,pw_req FROM history WHERE user_id = ? ORDER BY time DESC",
        user_id,
    )
    if query:
        pass
    else:
        return render_template("dashboard_empty.html")
    # code to convert sql time to human readable
    # for i in query:
    #     query[i]["time"] = query[i]["time"]
    return render_template("dashboard.html", query=query)


@app.route("/key", methods=["GET", "POST"])
def key():
    try:
        user_id = session["user_id"]
    except:
        user_id = 0
    if request.method == "POST":
        try:
            pkmn = (request.form["pkmn"]).lower()
            number = str(request.form["number"])
        except:
            key = request.form["key"]
        else:
            key = pkmn + "-" + number
        if key == "choose an option-":
            key = request.form["key"]
        pw = request.form["pw"]
    else:
        key = request.args.get("key")
        if key == None:
            return redirect("/")
        pw = ""
    try:
        pw2 = db.execute("SELECT pw FROM history WHERE key = ?", key)[0]["pw"]
        userid_2 = db.execute("SELECT user_id FROM history WHERE key = ?", key)[0][
            "user_id"
        ]
    except:
        flash("Invalid Keys", "red")
        return redirect("/")
    else:
        if check_password_hash(pw2, pw) or user_id == userid_2:
            query = db.execute(
                "SELECT title,key,lang,time,code FROM history WHERE key = ?", key
            )
            url = request.host_url + key
        else:
            if request.method == "POST":
                flash("Invalid Password", "red")
            else:
                flash("Password Required", "blue")
            return redirect("/pw_req?key=" + key)
    return render_template("key.html", query=query, url=url)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please Enter Username", "yellow")
            return redirect("/login")
        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please Enter Password", "red")
            return redirect("/login")
        username = request.form.get("username").lower().strip()
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        password = request.form.get("password")
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            flash("Invalid username and/or password", "red")
            return redirect("/login")
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        # Redirect user to home page
        flash("Login Successful, Welcome to CodeClip", "green")
        return redirect("/dashboard")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username").lower().strip()
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        if not username:
            flash("Please enter username!", "yellow")
            return redirect("/register")
        elif not password:
            flash("Please enter password!", "red")
            return redirect("/register")
        elif not confirmation:
            flash("Please re enter password!", "red")
            return redirect("/register")
        if password != confirmation:
            flash("Password does not match.", "red")
            return redirect("/register")
        # l, u, p, d = 0, 0, 0, 0
        s = password
        # capitalalphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        # smallalphabets = "abcdefghijklmnopqrstuvwxyz"
        # specialchar = "~`!@#$%^&*()_-+={[}]|\:;<,>.?/"
        # digits = "0123456789"
        if len(s) >= 8:
            #     for i in s:
            #         # counting lowercase alphabets
            #         if (i in smallalphabets):
            #             l += 1
            #         # counting uppercase alphabets
            #         if (i in capitalalphabets):
            #             u += 1
            #         # counting digits
            #         if (i in digits):
            #             d += 1
            #         # counting the mentioned special characters
            #         if (i in specialchar):
            #             p += 1
            # if (l >= 1 and u >= 1 and p >= 1 and d >= 1 and l+p+u+d == len(s)):
            hash = generate_password_hash(password)
            try:
                db.execute(
                    "INSERT INTO users(username, hash) VALUES (?,?)", username, hash
                )
            except:
                flash("Username taken already", "yellow")
                return redirect("/register")
            else:
                # Remember which user has logged in
                rows = db.execute("SELECT * FROM users WHERE username = ?", username)
                session["user_id"] = rows[0]["id"]
                # Redirect user to home page
                flash("Registration Successful, Welcome to CodeClip", "green")
                return redirect("/dashboard")
        else:
            # flash("Password does not meet all criteria", "red")
            flash("Password length is not sufficent", "red")
            return redirect("/register")
    else:
        return render_template("register.html")


@app.route("/delete")
@login_required
def delete():
    user_id = session["user_id"]
    key = request.args.get("key")
    try:
        user_id2 = db.execute("SELECT user_id FROM history WHERE key = ?", key)[0]["user_id"]
        if user_id == user_id2:
            db.execute("DELETE FROM history WHERE key = ? AND user_id= ?", key, user_id)
        else:
            flash("Illegal User", "yellow")
            return redirect("/dashboard")
    except:
        flash("Invalid Key", "yellow")
        return redirect("/dashboard")
    else:
        flash("Deletion Successful", "green")
    return redirect("/dashboard")


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    user_id = session["user_id"]
    if request.method == "POST":
        title = request.form.get("title")
        key = request.form.get("key")
        keynew = request.form.get("keynew")
        lang = request.form.get("lang")
        pw = request.form.get("pw")
        if pw == "":
            pw_req = 0
        else:
            pw_req = 1
        pw = generate_password_hash(request.form.get("pw"))
        code = request.form.get("code")
        if title == "":
            flash("Please enter a title", "yellow")
            return redirect("/dashboard")
        if code == "":
            flash("Please enter the code", "yellow")
            return redirect("/dashboard")
        try:
            db.execute(
                "UPDATE history SET title = ?, key = ?, lang = ? , code = ? , pw = ? , pw_req = ?, time = CURRENT_TIMESTAMP WHERE key = ? AND user_id = ? ",
                title,
                keynew,
                lang,
                code,
                pw,
                pw_req,
                key,
                user_id,
            )
        except:
            flash("Choose a different key.", "red")
            return redirect("/dashboard")
        flash("Update Successfully!", "green")
        return redirect("/dashboard")
    else:
        key = request.args.get("key")
        try:
            user_id2 = db.execute("SELECT user_id FROM history WHERE key = ?", key)[0]["user_id"]
            if user_id == user_id2:
                query = db.execute(
                    "SELECT title,key,lang,code FROM history WHERE key = ? AND user_id = ?",
                    key,
                    user_id,
                )
            else:
                flash("Illegal User", "yellow")
                return redirect("/dashboard")
        except:
            flash("Invalid Key", "yellow")
            return redirect("/dashboard")
        return render_template("update.html", query=query)


@app.route("/<key>")
def url_redirect(key):
    return redirect("/key?key=" + key)


@app.route("/pw_req")
def pw_req():
    key = request.args.get("key")
    return render_template("pw_req.html", key=key)


@app.route("/<key>/raw")
def raw_redirect(key):
    return redirect("/raw?key=" + key)


@app.route("/raw")
def raw():
    key = request.args.get("key")
    code = db.execute("SELECT code from history WHERE key = ?", key)[0]["code"]
    return render_template("raw.html", code=code)


@app.route("/test")
def test():
    return render_template("test2.html")
