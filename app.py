from flask import Flask, render_template, redirect, request, session
from flask_session import Session

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/saved")
def saved():
    return render_template("saved.html")

@app.route("/search")
def search():
    return render_template("search.hmtl")

@app.route("listen_later")
def listen_later():
    return render_template("listen_later.html")

