from flask import Flask, render_template, redirect, request, session, flash
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///music_app.db"
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username:
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
        user = users(username=username, password=hash)
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
        
        user = db.session.query(users).filter_by(name=username).first()
        if user is None or not check_password_hash(user.password, password): # checking for correct username and password
            flash("Invalid username or password")
            return render_template("login.html")
        
        session["user_id"] = user.id # storing the user id in session so we can remember who is currently logged in
        return render_template("index.html")
        
    else:
        return render_template("login.html")

@app.route("/saved")
def saved():
    return render_template("saved.html")

@app.route("/search")
def search():
    return render_template("search.hmtl")

@app.route("/listen_later")
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
    # This creates a link (a foreign key) back to the User who saved this album.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

with app.app_context():
    db.create_all()   # creates the tables inside of the "music_app" database 