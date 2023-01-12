import os
import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

pokemon = ["Arbok", "Arcanine", "Abra", "Alakazam", "Aerodactyl", "Articuno", "Bulbasaur", "Blastoise", "Butterfree", "Beedrill", "Bellsprout", "Charmander", "Charmeleon", "Charizard", "Caterpie", "Clefairy", "Clefable", "Cloyster", "Cubone", "Chansey", "Diglett", "Dugtrio", "Doduo", "Dodrio", "Dewgong", "Drowzee", "Ditto", "Dratini", "Dragonair", "Dragonite", "Ekans", "Electrode", "Exeggcute", "Exeggutor", "Electabuzz", "Eevee", "Fearow", "Farfetchd", "Flareon", "Golbat", "Gloom", "Golduck", "Growlithe", "Geodude", "Graveler", "Golem", "Grimer", "Gastly", "Gengar", "Goldeen", "Gyarados", "Haunter", "Hypno", "Hitmonlee", "Hitmonchan", "Horsea", "Ivysaur", "Jigglypuff", "Jynx", "Jolteon", "Kakuna", "Kadabra", "Krabby", "Kingler", "Koffing", "Kangaskhan", "Kabuto", "Kabutops", "Lickitung", "Lapras", "Metapod", "Meowth", "Mankey", "Machop",
           "Machoke", "Machamp", "Magnemite", "Magneton", "Muk", "Marowak", "Magmar", "Magikarp", "Moltres", "Mewtwo", "Mew", "Nidorina", "Nidoqueen", "Nidoran", "Nidorino", "Nidoking", "Ninetales", "Oddish", "Onix", "Omanyte", "Omastar", "Pidgey", "Pidgeotto", "Pidgeot", "Pikachu", "Paras", "Parasect", "Persian", "Psyduck", "Primeape", "Poliwag", "Poliwhirl", "Poliwrath", "Ponyta", "Pinsir", "Porygon", "Rattata", "Raticate", "Raichu", "Rapidash", "Rhyhorn", "Rhydon", "Squirtle", "Spearow", "Sandshrew", "Sandslash", "Slowpoke", "Slowbro", "Seel", "Shellder", "Seadra", "Seaking", "Staryu", "Starmie", "Scyther", "Snorlax", "Tentacool", "Tentacruel", "Tangela", "Tauros", "Venusaur", "Vulpix", "Vileplume", "Venonat", "Venomoth", "Victreebel", "Voltorb", "Vaporeon", "Wartortle", "Weedle", "Wigglytuff", "Weepinbell", "Weezing", "Zubat", "Zapdos"]


def gen_key():

    return ((random.choice(pokemon)).lower()+"-"+str(random.randint(100, 999)))


# Configure application
app = Flask(__name__)

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
    hash = (gen_key())
    if request.method == "POST":
        user_id = session["user_id"]
        title = request.form.get("title")
        key = request.form.get("key")
        lang = request.form.get("lang")
        pw = generate_password_hash(request.form.get("pw"))
        code = request.form.get("code")
        if title == "":
            flash("Please enter a title", "yellow")
            return redirect('/create')
        if key == "":
            flash("Please enter a key", "yellow")
            return redirect('/create')
        if code == "":
            flash("Please enter the code", "yellow")
            return redirect('/create')

        try:
            db.execute("INSERT INTO history (user_id ,title, key, lang ,code, pw) VALUES (? ,? ,? , ?, ?, ?)",
                       user_id, title, key, lang, code, pw)
        except:
            flash("Choose a different key.", "red")
            return redirect('/create')

        flash("Saved Successfully! Your key is " + key, "green")
        return redirect('/dashboard')

    else:
        return render_template("create.html", hash=hash)


@app.route("/dashboard")
@login_required
def dashboard():

    user_id = session["user_id"]
    query = db.execute(
        "SELECT title,key,lang,code,time,pw FROM history WHERE user_id = ? GROUP BY time ORDER BY time DESC", user_id)
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
    if request.method == "POST":
        pkmn = (request.form['pkmn']).lower()
        number = str(request.form['number'])
        key = (pkmn+"-"+number)

        # if pkmn == "pokemon":
        #     flash("Please choose a pokemon", "yellow")
        #     return redirect("/")
        # if number == "":
        #     flash("Please enter the number", "yellow")
        #     return redirect("/")

        if key == "choose an option-":
            key = request.form['key']
        pw = request.form['pw']

    else:
        key = request.args.get("key")
        pw = request.args.get("pw")
        if key == None or key == "":
            flash("Please enter a key", "yellow")
            return redirect("/")

    query = ""

    try:
        pw2 = db.execute("SELECT pw FROM history WHERE key = ?", key)[
            0]["pw"]
    except:
        flash("Invalid Keys", "red")
        return redirect("/")

    else:
        if check_password_hash(pw2, pw):
            query = db.execute(
                "SELECT title,key,lang,time,code FROM history WHERE key = ?", key)
        elif pw2 == pw:
            query = db.execute(
                "SELECT title,key,lang,time,code FROM history WHERE key = ?", key)
        else:
            flash("Incorrect Password", "red")
            return redirect("/")

    return render_template("key.html", query=query)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    # session.clear()

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

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?",
                          request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
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
    if (request.method == "POST"):
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if not username:
            flash('Please enter username!', 'yellow')
            return redirect("/register")
        elif not password:
            flash('Please enter password!', 'red')
            return redirect("/register")
        elif not confirmation:
            flash('Please re enter password!', 'red')
            return redirect("/register")

        if password != confirmation:
            flash('Password does not match.', 'red')
            return redirect("/register")

        # l, u, p, d = 0, 0, 0, 0
        s = password
        # capitalalphabets = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        # smallalphabets = "abcdefghijklmnopqrstuvwxyz"
        # specialchar = "~`!@#$%^&*()_-+={[}]|\:;<,>.?/"
        # digits = "0123456789"
        if (len(s) >= 8):
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
                    "INSERT INTO users(username, hash) VALUES (?,?)", username, hash)
            except:
                flash('Username taken already', 'yellow')
                return redirect("/register")
            else:
                # Remember which user has logged in
                rows = db.execute("SELECT * FROM users WHERE username = ?",
                                  username)

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

    key = request.args.get("key")
    pw = request.args.get("pw")
    user_id = session["user_id"]

    try:
        db.execute(
            "DELETE FROM history WHERE key = ? AND pw = ? AND user_id= ?", key, pw, user_id)
    except:
        flash("Does Not Exist", "yellow")
    else:
        flash("Deletion Successful", "green")

    return redirect('/dashboard')


@app.route("/update", methods=["GET", "POST"])
@login_required
def update():
    user_id = session["user_id"]
    if request.method == "POST":
        title = request.form.get("title")
        key = request.form.get("key")
        keynew = request.form.get("keynew")
        lang = request.form.get("lang")
        pw = generate_password_hash(request.form.get("pw"))
        code = request.form.get("code")
        if title == "":
            flash("Please enter a title", "yellow")
            return redirect('/dashboard')
        if code == "":
            flash("Please enter the code", "yellow")
            return redirect('/dashboard')
        try:
            db.execute("UPDATE history SET title = ?, key = ?, lang = ? , code = ? , pw = ?  WHERE key = ? AND user_id = ? ",
                       title, keynew, lang, code, pw, key, user_id)
        except:
            flash("Choose a different key.", "red")
            return redirect('/dashboard')

        flash("Update Successfully!", "green")
        return redirect('/dashboard')
    else:
        key = request.args.get("key")
        pw = request.args.get("pw")

        try:
            pw2 = db.execute("SELECT pw FROM history WHERE key = ? AND user_id = ?", key, user_id)[
                0]["pw"]
        except:
            flash("Invalid Key", "yellow")
            return redirect('/dashboard')
        else:
            if pw2 == pw:
                query = db.execute(
                    "SELECT title,key,lang,code FROM history WHERE key = ? AND user_id = ?", key, user_id)
            else:
                flash("Invalid Hashes", "yellow")
                return redirect('/dashboard')

        return render_template("update.html", query=query)
