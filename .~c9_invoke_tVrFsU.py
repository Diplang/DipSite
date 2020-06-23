import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd
from dreamscript import *
from parser import *
from datetime import datetime
import psycopg2

# Configure application
app = Flask(__name__)
usrname = ""

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Use SQLite database
db =  SQL("postgres://yagqggxlzasyks:dd4225e4d6b34be3409ea16e9d16240403c1cfccd94decc86c8e87703ee8f5c8@ec2-52-0-155-79.compute-1.amazonaws.com:5432/d3026drc6so9qe")


@app.route("/")
def index():
    """Show Homepage"""
    return render_template("index.html")

@app.route("/signup", methods=['GET', 'POST'])
def register():
    """Register user"""
    if request.method == "POST":

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))


        # Ensure username doesn 't exist
        if len(rows) == 1:
            return apology("Username already exists", 403)

        usrname = request.form.get("username")

        pword = request.form.get("password")

        conn = psycopg2.connect("postgres://yagqggxlzasyks:dd4225e4d6b34be3409ea16e9d16240403c1cfccd94decc86c8e87703ee8f5c8@ec2-52-0-155-79.compute-1.amazonaws.com:5432/d3026drc6so9qe")
        cur = conn.cursor()

        query = """INSERT INTO users (username, hash) VALUES (%s,%s)"""
        info = (usrname, generate_password_hash(pword))

        # add user into database
        user = cur.execute(query, info)

        conn.commit()

        return redirect("/login")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("signup.html")

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Log user in"""

    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        print(rows)


        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("No account exists with these credentials", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        session["username"] = rows[0]["username"]


        # Redirect user to home page
        return redirect("/forum")


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

@app.route("/upload", methods=['GET', 'POST'])
@login_required
def upload():
    """Upload a new project"""
    if request.method == "POST":
        print("HELLOOOOO")
        url = request.form.get("url")
        name = request.form.get("title")
        status = request.form.get("snips")
        description = request.form.get("description")
        github = request.form.get("code")

        username = session.get("username")

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=name)
        # Ensure project doesn't exist
        if len(rows) == 1:
            return apology("Project already exists", 403)

        project = db.execute("INSERT INTO projects (url, name, description, github, screenshot) VALUES (:url, :name, :description, :github,:screenshot)", url=request.form.get("url"), name=request.form.get("title"),description=request.form.get("description"), github = request.form.get("code"), screenshot = request.form.get("snips"))

        return redirect(f"/projects/{name}/")
    else:
        return render_template("upload.html")




@app.route("/forum", methods=['GET', 'POST'])
def forum():

    posts = []


    rows = db.execute("SELECT * FROM posts")

    for index, row in enumerate(rows):
        op = db.execute("SELECT * FROM comments WHERE post_id = :identification",
                          identification=row["id"])
        posts.append(list((row["title"], row["description"], row['id'], row['author'], row['timestamp'], len(op))))

        print(op)
    return render_template("forum.html",posts=posts)


@app.route("/newest", methods=['GET', 'POST'])
def newest():

    posts = []


    rows = db.execute("SELECT * FROM posts ORDER BY timestamp DESC")


    for index, row in enumerate(rows):
        op = db.execute("SELECT * FROM comments WHERE post_id = :identification",
                          identification=row["id"])
        posts.append(list((row["title"], row["description"], row['id'], row['author'], row['timestamp'], len(op))))


    return render_template("newest.html",posts=posts)

@app.route("/comments", methods=['GET', 'POST'])
def comments():

    posts = []

    rows = db.execute("SELECT * FROM comments ORDER BY timestamp DESC")

    print(rows)


    for index, row in enumerate(rows):
        print(row)
        query = """SELECT title FROM posts WHERE id = :identification"""

        op = db.execute("SELECT title FROM posts WHERE id = :identification", identification=row["post_id"])

        print(row["content"])
        print(row["author"])
        print(row["post_id"])
        print(row["timestamp"])
        print(op[0]["title"])

        posts.append(list((row["content"], row["author"], row["post_id"], row["timestamp"], op[0]["title"])))




    return render_template("comments.html",posts=posts)


@app.route("/submit", methods=['GET', 'POST'])
def submit():
    """Submit post"""
    print("forum: ", session.get("username"))

    if request.method == "POST":

        author = session.get("username")


        title = request.form.get("title")

        text = request.form.get("text")

        print(datetime.now())

        if session.get("username") == None:
            return redirect("/login")

        conn = psycopg2.connect("postgres://yagqggxlzasyks:dd4225e4d6b34be3409ea16e9d16240403c1cfccd94decc86c8e87703ee8f5c8@ec2-52-0-155-79.compute-1.amazonaws.com:5432/d3026drc6so9qe")
        cur = conn.cursor()

        query = """INSERT INTO posts (author, title, description, timestamp) VALUES (%s, %s, %s, %s)"""
        info = (author, title, text, datetime.now())

        # add user into database
        post = cur.execute(query, info)

        conn.commit()


        # add post into database
        #post = db.execute("INSERT INTO posts (author, title, description, timestamp) VALUES (:author, :title, :text, :timestamp)", author=author, title=title, text=formatted_text, timestamp=datetime.now())

        return redirect("/forum")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("submit.html")



@app.route("/docs")
def docs():
    return render_template("docs.html")

@app.route("/posts/<iden>", methods=['GET', 'POST'])
def individual(iden):

    comments_list = []

    iden = db.execute("SELECT id FROM posts WHERE id = :identification",
                          identification=iden)

    title = db.execute("SELECT title FROM posts WHERE id = :identification",
                          identification=iden[0]["id"])

    description = db.execute("SELECT description FROM posts WHERE id = :identification",
                          identification=iden[0]["id"])

    author = db.execute("SELECT author FROM posts WHERE id = :identification",
                          identification=iden[0]["id"])

    timestamp = db.execute("SELECT timestamp FROM posts WHERE id = :identification",
                          identification=iden[0]["id"])

    comments_ = db.execute("SELECT * FROM comments WHERE post_id = :identification",
                          identification=iden[0]["id"])

    for index, row in enumerate(comments_):
        comments_list.append(list((row["content"], row["author"], row['timestamp'])))


    if request.method == "POST":
        if session.get("username") == None:
            return redirect("/login")

        content = request.form.get("description")

        conn = psycopg2.connect("postgres://yagqggxlzasyks:dd4225e4d6b34be3409ea16e9d16240403c1cfccd94decc86c8e87703ee8f5c8@ec2-52-0-155-79.compute-1.amazonaws.com:5432/d3026drc6so9qe")
        cur = conn.cursor()

        query = """INSERT INTO comments (post_id, author, content, timestamp) VALUES (%s, %s, %s, %s)"""
        info = (iden[0]["id"], session.get("username"), content, datetime.now())

        # add user into database
        user = cur.execute(query, info)

        conn.commit()

        return redirect("/posts/" + str(iden[0]["id"]))

    if len(comments_) == 0:
        return render_template("post.html", iden=iden[0]["id"], title=title[0]["title"], description=description[0]["description"], author=author[0]["author"], timestamp=timestamp[0]["timestamp"], commentsnum=0)

    print(comments_[0]["content"])
    return render_template("post.html", iden=iden[0]["id"], title=title[0]["title"], description=description[0]["description"], author=author[0]["author"], timestamp=timestamp[0]["timestamp"], comments=comments_list, commentsnum=len(comments_))

@app.route("/start")
def start():
    return render_template("start.html")

@app.route("/try", methods=['GET', 'POST'])
def trydip():
    inputt = ""
    if request.method == "POST":

        print("\nDip Version 0.1 - Beta\n")
        print('\nType "help", "copyright", "credits" or "about" for more information.\n')
        raw_text = str(request.form.get("input"))

        formatted_text = raw_text.replace("\r", "")

        result, error = run('<input>', formatted_text)

        print(raw_text)

        if str(request.form.get("input")) == "":
            inputt = 'print("Hello, Dip!")'
        else:
            inputt = str(request.form.get("input"))


        if error:
            return render_template("try.html", inputt=inputt, error=(error.as_string()))

        elif result:
            return render_template("try.html", inputt=inputt, output=list(result.elements))
    else:
        return render_template("try.html", inputt=inputt)

@app.route("/about")
def about():
    """Show About page"""
    return render_template("about.html")


@app.route("/install")
def install():
    """Show Install page"""
    return render_template("install.html")