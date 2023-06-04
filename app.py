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
    return render_template("patient/home-patient.html")

#halaman form janji temu / appointment
@app.route("/appointment", methods=["GET"])
def appointment():
    return render_template("patient/appointment.html")

# Halaman Info User Pasien
# @app.route("/patient/<email>", methods=["GET"])
# def user(email):
#     token_receive = request.cookies.get(TOKEN_KEY)
#     try:
#         payload = jwt.decode(
#             token_receive,
#             SECRET_KEY,
#             algorithms=["HS256"]
#         )
#         status= email == payload.get("id")
#         patient_info = db.patient.find_one(
#             {"email" : email},
#             {"_id" : False}
#             )
#         return render_template("user-patient.html", 
#                         patient_info=patient_info,
#                         status=status)
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))
@app.route("/info-patient", methods=["GET"])
def info_patient():
    return render_template("patient/info-patient.html")

# Halaman Edit User Pasien
# @app.route("/update_profile", methods=["POST"])
# def update_profile():
#     token_receive = request.cookies.get(TOKEN_KEY)
#     try:
#         payload = jwt.decode(
#             token_receive,
#             SECRET_KEY,
#             algorithms=["HS256"]
#         )
#         username = payload.get("id")
#         name_receive = request.form.get("name_give")
#         about_receive = request.form.get("about_give")
        
#         new_doc = {
#             "profile_name" : name_receive,
#             "profile_info" : about_receive
#         }
        
#         if "file_give" in request.files:
#             file = request.files.get("file_give")
#             filename = secure_filename(file.filename)
#             extension = filename.split(".")[-1]
#             file_path = f"profile_pics/{username}.{extension}"
#             file.save("./static/" + file_path)
#             new_doc["profile_pic"] = filename
#             new_doc["profile_pic_real"] = file_path

#         db.user.update_one(
#             {"username" : username},
#             {"$set" : new_doc}
#         )
#         db.posts.update_one(
#             {"username" : username},
#             {"$set" : new_doc}
#         )
#         return jsonify({
#             "result" : "success",
#             "msg" : "Your profile has been updated"
#         })
#     except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
#         return redirect(url_for("home"))
@app.route("/edit-patient")
def edit_pasien():
    return render_template("patient/user-patient.html")

#List patient Appointment with doctor
@app.route("/appointment-doctor")
def appointment_doctor():
    return render_template("patient/appointment-doctor.html")

#doctor page for patient navbar
@app.route("/doctor-homepatient")
def doctor_homepatient():
    return render_template("patient/doctor-homepatient.html")

#doctor item page for patient navbar
@app.route("/doctor-item-homepatient")
def doctor_item_homepatient():
    return render_template("patient/doctor-item-homepatient.html")

#blog page for patient navbar
@app.route("/blog-homepatient")
def blog_homepatient():
    return render_template("patient/blog-homepatient.html")

#blog item page for patient navbar
@app.route("/blog-post-homepatient")
def blog_post_homepatient():
    return render_template("patient/blog-post-homepatient.html")

#home page for doctor
@app.route("/home-doctor")
def home_doctor():
    return render_template("doctor/home-doctor.html")

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)