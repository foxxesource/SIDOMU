from flask import Flask, render_template, redirect, url_for, request, jsonify
from pymongo import MongoClient
import jwt
from dotenv import load_dotenv
import os
from os.path import join, dirname
from werkzeug.utils import secure_filename

app = Flask(__name__)

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

MONGODB_URL = os.environ.get("MONGODB_URL")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URL)
db = client[DB_NAME]

SECRET_KEY = "finalproject"

TOKEN_KEY= "mytoken"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/hospitals", methods=["GET"])
def hospitals():
    return render_template("hospital.html")

@app.route("/hospital1", methods=["GET"])
def hospital1():
    return render_template("hospitals-item.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")
    
@app.route("/login/doctor")
def login_doctor():
    return render_template("login-doctor.html")

@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)