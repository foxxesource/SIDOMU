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

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

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
    
@app.route("/login-doctor")
def login_doctor():
    return render_template("login-doctor.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/doctor")
def doctor():
    return render_template("doctor.html")

@app.route("/doctor-item")
def doctor_item():
    return render_template("doctors-item.html")

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/blog-post")
def blog_post():
    return render_template("blog-post.html")

# Halaman Pasien
@app.route("/home-patient", methods=["GET"])
def home_patient():
    return render_template("home-patient.html")

#halaman janji temu / appointment
@app.route("/appointment", methods=["GET"])
def appointment():
    return render_template("appointment.html")

# Halaman Edit User Pasien
@app.route("/patient/<email>", methods=["GET"])
def user(email):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        status= email == payload.get("id")
        patient_info = db.patient.find_one(
            {"email" : email},
            {"_id" : False}
            )
        return render_template("user-patient.html", 
                        patient_info=patient_info,
                        status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)