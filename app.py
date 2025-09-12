from flask import Flask, render_template, redirect, request, session, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
from functools import wraps
import json
import requests

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///music_app.db"
db = SQLAlchemy(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:   # no user logged in
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username1 = request.form.get("username")
        password = request.form.get("password")
        if not username1:
            flash("Must provide a username")
            return render_template("register.html")
        elif not password:
            flash("Must provide password")
            return render_template("register.html")
        elif not request.form.get("confirmation"):
            flash("Must enter confirmation password")
            return render_template("register.html")
        elif password != request.form.get("confirmation"):
            flash("Passwords do not match")
            return render_template("register.html")
        
        hash = generate_password_hash(password)
        user = users(username=username1, password=hash)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError: # username column is unique so IntegrityError occurs if username already exists
            flash("Username already exists")
            return render_template("register.html")
        
        return render_template("login.html")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
            flash("Must provide username")
            return render_template("login.html")
        elif not password:
            flash("Must provide password")
            return render_template("login.html")
        
        user = db.session.query(users).filter_by(username=username).first()
        if user is None or not check_password_hash(user.password, password): # checking for correct username and password
            flash("Invalid username or password")
            return render_template("login.html")
        
        session["user_id"] = user.id # storing the user id in session so we can remember who is currently logged in
        return render_template("index.html")
        
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("login.html")

@app.route("/saved")
@login_required
def saved():
    return render_template("saved.html")

@app.route("/search", methods=["POST", "GET"])
@login_required
def search():
    albums = []
    if request.method == "POST":
        query = request.form.get("album")
        response = requests.get(f"https://musicbrainz.org/ws/2/release/?query={query}&fmt=json")
        if response.status_code == 200:
            data = response.json()
            
            for release in data:
                title = release.get("title", "N/A")
                artist = release.get("artist-credit", [{}])[0].get("artist", {}).get("name", "Unknown")
    return render_template("search.html")

@app.route("/listen_later")
@login_required
def listen_later():
    return render_template("listen_later.html")

class users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False) # The hash of the password will be stored, not the text

class albums(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)
    rating = db.Column(db.Float, nullable=True)
    listen_later = db.Column(db.Boolean, default=False)
    # This creates a link (a foreign key) back to the User who saved this album.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

with app.app_context():
    db.create_all()   # creates the tables inside of the "music_app" database 
