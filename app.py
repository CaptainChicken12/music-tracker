from flask import Flask, render_template, redirect, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///music_app.db"
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("index.html")

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
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False) # The hash of the password will be stored, not the text

class albums(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artist = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    year = db.Column(db.String, nullable=False)
    # This creates a link (a foreign key) back to the User who saved this album.
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

with app.app_context():
    db.create_all()   # creates the tables inside of the "music_app" database 