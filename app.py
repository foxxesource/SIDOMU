from flask import Flask, render_template, redirect, url_for, request, jsonify
from pymongo import MongoClient
import jwt
# pip install PyJWT==1.7.0
from dotenv import load_dotenv
import os
from os.path import join, dirname
from datetime import datetime, timedelta
import hashlib
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

SECRET_KEY = "BINTANGSAH123"

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

@app.route("/login", methods=["GET"])
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

#sign in
@app.route("/sign_in", methods=["POST"])
def sign_in():
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.user_patient.find_one(
        {
            "email": email_receive,
            "password": pw_hash,
        }
    )
    if result:
        payload = {
            "id": email_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    # Let's also handle the case where the id and
    # password combination cannot be found
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that email/password combination",
            }
        )

#register patient
@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    fname_receive = request.form.get("fname_give")
    lname_receive = request.form.get("lname_give")
    email_receive = request.form.get("email_give")
    password_receive = request.form.get("password_give")
    password_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    exists = bool(db.user_patient.find_one({"email" : email_receive}))
    doc = {
        "first_name" : fname_receive,
        "last_name" : lname_receive,
        "email" : email_receive,
        "password" : password_hash,
        "profile_name" : fname_receive,
        "profile_pic" : "",
        "profile_pic_real" : "profile_pics/profile_placeholder.png",
        "additional_details" : "",
        "age" : "",
        "mobile_number" : "",
        "country" : "",
        "state_region" : ""
    }
    db.user_patient.insert_one(doc)
    return jsonify({"result" : "success", "exists" : exists})

#CHECK EMAIL DUPLICATE ON SIGN UP
@app.route("/sign_up/check_dup", methods=["POST"])
def check_dup():
    email_receive = request.form.get("email_give")
    exists = bool(db.user_patient.find_one({"email" : email_receive}))
    return jsonify({"result" : "success", "exists" : exists}) 
    
@app.route("/login-doctor")
def login_doctor():
    msg = request.args.get("msg")
    return render_template("login-doctor.html", msg=msg)

#sign in doctor
@app.route("/sign_in_doctor", methods=["POST"])
def sign_in_doctor():
    email_receive = request.form["email_give"]
    password_receive = request.form["password_give"]
    result = db.user_doctor.find_one(
        {
            "email": email_receive,
            "password": password_receive,
        }
    )
    if result:
        payload = {
            "id": email_receive,
            # the token will be valid for 24 hours
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY)

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    # Let's also handle the case where the id and
    # password combination cannot be found
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that email/password combination",
            }
        )

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
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        return render_template("patient/home-patient.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("home",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("home",msg=msg))

#halaman form janji temu / appointment
@app.route("/appointment", methods=["GET"])
def appointment():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        return render_template("patient/appointment.html", user_info = user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

#server save appointment
@app.route("/appointment/save", methods=["POST"])
def appointment_save():
    fname_receive = request.form.get("fname_give")
    lname_receive = request.form.get("lname_give")
    mobilenumber_receive = request.form.get("mobilenumber_give")
    doctor_receive = request.form.get("doctor_give")
    email_receive = request.form.get("email_give")
    message_receive = request.form.get("message_give")
    # exists = bool(db.user_patient.find_one({"email" : email_receive}))
    doc = {
        "first_name" : fname_receive,
        "last_name" : lname_receive,
        "mobile_number" : mobilenumber_receive,
        "doctor" : doctor_receive,
        "email" : email_receive,
        "message" : message_receive
    }
    db.appointment_patient.insert_one(doc)
    return jsonify({"result" : "success"})


# @app.route("/info-patient", methods=["GET"])
# def info_patient():
#     return render_template("patient/info-patient.html")

#Halaman Edit Profile Patient
@app.route("/user-patient/<email>", methods=["GET"])
def user_patient(email):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one(
            {"email" : email},
            {"_id" : False}
            )
        return render_template("patient/user-patient.html", user_info = user_info)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


# Server Side Edit User Pasien
@app.route("/update_profile", methods=["POST"])
def update_profile():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        email = payload.get("id")
        fname_receive = request.form.get("fname_give")
        lname_receive = request.form.get("lname_give")
        mobilenumber_receive = request.form.get("mobilenumber_give")
        country_receive = request.form.get("country_give")
        stateregion_receive = request.form.get("stateregion_give")
        age_receive = request.form.get("age_give")
        additionaldetails_receive = request.form.get("additionaldetails_give")
        new_doc = {
            "first_name" : fname_receive,
            "last_name" : lname_receive,
            "mobile_number" : mobilenumber_receive,
            "country" : country_receive,
            "state_region" : stateregion_receive,
            "age" : age_receive,
            "additional_details" : additionaldetails_receive,
        }
        
        if "file_give" in request.files:
            file = request.files.get("file_give")
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{email}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path

        db.user_patient.update_one(
            {"email" : email},
            {"$set" : new_doc}
        )
        # db.posts.update_one(
        #     {"email" : email},
        #     {"$set" : new_doc}
        # )
        return jsonify({
            "result" : "success",
            "msg" : "Your profile has been updated"
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))
    
@app.route("/info-patient/<email>", methods=["GET"])
def info_patient(email):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        status= email == payload.get("id")
        user_info = db.user_patient.find_one(
            {"email" : email},
            {"_id" : False}
            )
        return render_template("patient/info-patient.html", 
                        user_info=user_info,
                        status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
         return redirect(url_for("home"))

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
@app.route("/blog-homepatient", methods=["GET"])
def blog_homepatient():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        return render_template("patient/blog-homepatient.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("home",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("home",msg=msg))

#blog item page for patient navbar
@app.route("/blog-post-homepatient")
def blog_post_homepatient():
    return render_template("patient/blog-post-homepatient.html")

#home page for doctor
@app.route("/home-doctor")
def home_doctor():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
        )
        user_info = db.user_doctor.find_one({"email" : payload.get("id")})
        return render_template("patient/home-doctor.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login_doctor",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login_doctor",msg=msg))

#list schedule for doctor
@app.route("/appointment-patient")
def appointment_patient():
    return render_template("doctor/appointment-patient.html")

#User info for doctor
@app.route("/info-doctor")
def info_doctor():
    return render_template("doctor/info-doctor.html")

#User edit for doctor
@app.route("/edit-doctor")
def user_doctor():
    return render_template("doctor/user-doctor.html")

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)