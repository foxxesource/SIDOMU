from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from pymongo import MongoClient
import jwt
import certifi
# pip install PyJWT==1.7.0
from dotenv import load_dotenv
import os
from os.path import join, dirname
from datetime import datetime, timedelta
import hashlib
from datetime import datetime, timedelta
import json
from bson.objectid import ObjectId
from werkzeug.utils import secure_filename

app = Flask(__name__)

dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

MONGODB_URL = os.environ.get("MONGODB_URL")
DB_NAME = os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URL,  tlsCAFile=certifi.where() )
db = client[DB_NAME]

SECRET_KEY = "BINTANGSAH123"

TOKEN_KEY = "mytoken"
app.secret_key = 'your_secret_key'

TOKEN_KEY2 = "mytoken2"

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
        session['email_patient'] = email_receive

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
        session['email_doctor'] = email_receive
    
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

@app.route("/get_doc", methods=["GET"])
def get_doc():
    doc_info = list(db.user_doctor.find({}, {"_id" : False}))
    return jsonify({"result" : "success",
            "msg" : "successfully fetched all doctors",
            "doc_info" : doc_info,})

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
    docemail_receive = request.form.get("doctorval_give")
    message_receive = request.form.get("message_give")
    date_receive = request.form.get("date_give")
    count = db.appointment_patient.count_documents({})
    num = count + 1
    # exists = bool(db.user_patient.find_one({"email" : email_receive}))
    doc = {
        "num" : num,
        "first_name" : fname_receive,
        "last_name" : lname_receive,
        "mobile_number" : mobilenumber_receive,
        "doctor" : doctor_receive,
        "email" : email_receive,
        "doc_email" : docemail_receive,
        "message" : message_receive,
        "status" : 0,
        "doc_message" : "",
        "date_app" : "",
        "timestart_app" : "",
        "timeend_app" : "",
        "date" : date_receive
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
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        return render_template("patient/appointment-doctor.html", user_info = user_info
                                                                )
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("home",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("home",msg=msg))

#get appointment from patient
@app.route("/get_app", methods=["GET"])
def get_app():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        email_receive = request.args.get("email_give")    
        apps = list(db.appointment_patient.find({"email" : email_receive}, {"_id" : False}).sort("date", -1).limit(9))
        for app in apps:
            data2 = db.user_doctor.find_one({"legit_doctorname" : app["doctor"]})
            app["doctor_firstName"] = data2["first_name"]
            app["doctor_lastName"] = data2["last_name"]
            app["doctor_specialist"] = data2["specialist"]
            app["doctor_profilePicture"] = data2["profile_pic_real"]

        return jsonify({
            "result" : "success",
            "msg" : "successfully fetched all appointments",
            "apps" : apps,
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

#doctor page for patient navbar
@app.route("/doctor-homepatient")
def doctor_homepatient():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        return render_template("patient/doctor-homepatient.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("home",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("home",msg=msg))
    
#get doctor data from database
@app.route("/get_doctor", methods=["GET"])
def get_doctor():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        doc_info = list(db.user_doctor.find({}, {"_id" : False}))
        return jsonify({
            "result" : "success",
            "msg" : "successfully fetched all doctors",
            "doc_info" : doc_info,
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

#doctor item1 page for patient navbar
@app.route("/doctor-item1-homepatient")
def doctor_item_homepatient():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        doct1_info = db.user_doctor.find_one({"email" : "bintang.duinata311@gmail.com"})
        return render_template("patient/doctor-item1-homepatient.html", user_info = user_info
                                                                      , doct1_info = doct1_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("home",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("home",msg=msg))
    
@app.route("/doctor-item2-homepatient")
def doctor_item2_homepatient():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        doct1_info = db.user_doctor.find_one({"email" : "drRizkiKandias@gmail.com"})
        return render_template("patient/doctor-item2-homepatient.html", user_info = user_info
                                                                      , doct1_info = doct1_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("home",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("home",msg=msg))
    
@app.route("/doctor-item3-homepatient")
def doctor_item3_homepatient():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        doct1_info = db.user_doctor.find_one({"email" : "drSriRaihanPutri@gmail.com"})
        return render_template("patient/doctor-item3-homepatient.html", user_info = user_info
                                                                      , doct1_info = doct1_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("home",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("home",msg=msg))

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

@app.route("/blog-post-homepatient")
def blog_post_homepatient():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        return render_template("patient/blog-post-homepatient.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("home",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("home",msg=msg))

   
#blog item page for patient navbar
@app.route("/hospitals-homepatient")
def hospitals_homepatient():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        return render_template("patient/hospitals-homepatient.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("home",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("home",msg=msg))
    
@app.route("/hospitals-item-homepatient")
def hospitals_item_homepatient():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        return render_template("patient/hospitals-item-homepatient.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("home",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("home",msg=msg))

#home page for doctor
@app.route("/home-doctor")
def home_doctor():
    token_receive = request.cookies.get(TOKEN_KEY2)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_doctor.find_one({"email" : payload.get("id")})
        return render_template("doctor/home-doctor.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login_doctor",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login_doctor",msg=msg))

#list schedule for doctor
@app.route("/appointment-patient")
def appointment_patient():
    token_receive = request.cookies.get(TOKEN_KEY2)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_doctor.find_one({"email" : payload.get("id")})
        return render_template("doctor/appointment-patient.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login_doctor",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login_doctor",msg=msg))

#get appointment from patient to doctor
@app.route("/get_app_patient", methods=["GET"])
def get_app_patient():
    token_receive = request.cookies.get(TOKEN_KEY2)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        email_receive = request.args.get("email_give")    
        apps = list(db.appointment_patient.find({"doc_email" : email_receive}).sort("date", -1).limit(20))
        
        for app in apps:
            app["_id"] = str(app["_id"])
            data2 = db.user_patient.find_one({"email" : app["email"]})
            app["patient_firstName"] = data2["first_name"]
            app["patient_lastName"] = data2["last_name"]
            app["patient_country"] = data2["country"]
            app["patient_stateRegion"] = data2["state_region"]
            app["patient_pfp"] = data2["profile_pic_real"]
        

        return jsonify({
            "result" : "success",
            "msg" : "successfully fetched all appointments",
            "apps" : apps,
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

#accept appointment from doctor
@app.route("/update_appointment", methods=["POST"])
def update_appointment():
    token_receive = request.cookies.get(TOKEN_KEY2)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        message_receive = request.form.get("message_give")
        date_receive = request.form.get("date_give")
        time1_receive = request.form.get("time1_give")
        time2_receive = request.form.get("time2_give")
        id_receive = request.form.get("id_give")
        new_doc = {
            "doc_message" : message_receive,
            "date_app" : date_receive,
            "timestart_app" : time1_receive,
            "timeend_app" : time2_receive,
            "status" : 1
        }

        db.appointment_patient.update_one(
            {"_id" : ObjectId(id_receive)},
            {"$set" : new_doc}
        )
        return jsonify({
            "result" : "success",
            "msg" : "Appointment Accepted"
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

#cancel appointment from doctor
@app.route("/cancel_appointment", methods=["POST"])
def cancel_appointment():
    token_receive = request.cookies.get(TOKEN_KEY2)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        message_receive = request.form.get("message_give")
        id_receive = request.form.get("id_give")
        new_doc = {
            "doc_message" : message_receive,
            "status" : 3
        }

        db.appointment_patient.update_one(
            {"_id" : ObjectId(id_receive)},
            {"$set" : new_doc}
        )
        return jsonify({
            "result" : "success",
            "msg" : "Appointment Declined"
        })
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))

#User info for doctor
@app.route("/info-doctor")
def info_doctor():
    token_receive = request.cookies.get(TOKEN_KEY2)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_doctor.find_one({"email" : payload.get("id")})
        return render_template("doctor/info-doctor.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login_doctor",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login_doctor",msg=msg))

#User edit for doctor
@app.route("/edit-doctor")
def user_doctor():
    token_receive = request.cookies.get(TOKEN_KEY2)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_doctor.find_one({"email" : payload.get("id")})
        return render_template("doctor/user-doctor.html", user_info = user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login_doctor",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login_doctor",msg=msg))

#doctor server edit
@app.route("/update_docprofile", methods=["POST"])
def update_docprofile():
    token_receive = request.cookies.get(TOKEN_KEY2)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        email = payload.get("id")
        mobilenumber_receive = request.form.get("mobilenumber_give")
        country_receive = request.form.get("country_give")
        stateregion_receive = request.form.get("stateregion_give")
        twitter_receive = request.form.get("twitter_give")
        facebook_receive = request.form.get("facebook_give")
        linkedin_receive = request.form.get("linkedin_give")
        youtube_receive = request.form.get("youtube_give")
        additionaldetails_receive = request.form.get("additionaldetails_give")
        new_doc = {
            "phone_number" : mobilenumber_receive,
            "address_country" : country_receive,
            "address_stateregion" : stateregion_receive,
            "twitter" : twitter_receive,
            "facebook" : facebook_receive,
            "linkedin" : linkedin_receive,
            "youtube" : youtube_receive,
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

        db.user_doctor.update_one(
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

@app.route('/chat')
def chat():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        email = session['email_patient']
        users = db.user_doctor.find({'email': {'$ne': email}})
        return render_template('patient/chat.html', email=email, users=users, user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login",msg=msg))
    
@app.route('/chat_doc')
def chat_doc():
    token_receive = request.cookies.get(TOKEN_KEY2)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_doctor.find_one({"email" : payload.get("id")})
        email = session['email_doctor']
        users = db.user_patient.find({'email': {'$ne': email}})
        return render_template('doctor/chat_doc.html', email=email, users=users, user_info=user_info)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login",msg=msg))
   
    
@app.route('/chat/<friend>')
def private_chat(friend):
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_patient.find_one({"email" : payload.get("id")})
        email = session['email_patient']
        friend = db.user_doctor.find_one({'email': friend})
        messages = db.messages.find({
        '$or': [
            {'sender': email, 'receiver': friend['email']},
            {'sender': friend['email'], 'receiver': email}
        ]
        }).sort('timestamp', 1)
        return render_template("patient/private_chat.html", user_info = user_info,
                               email=email, 
                               friend=friend, 
                               messages=messages)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login",msg=msg))

@app.route('/chat_doc/<friend>')
def private_chat_doc(friend):
    token_receive = request.cookies.get(TOKEN_KEY2)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=["HS256"]
        )
        user_info = db.user_doctor.find_one({"email" : payload.get("id")})
        email = session['email_doctor']
        friend = db.user_patient.find_one({'email': friend})
        messages = db.messages.find({
        '$or': [
            {'sender': email, 'receiver': friend['email']},
            {'sender': friend['email'], 'receiver': email}
        ]
        }).sort('timestamp', 1)
        return render_template("doctor/private_chat_doc.html", user_info = user_info,
                               email=email, 
                               friend=friend, 
                               messages=messages)
    except jwt.ExpiredSignatureError:
        msg = "Your token has expired"
        return redirect(url_for("login",msg=msg))
    except jwt.exceptions.DecodeError:
        msg = "There was a problem logging your in"
        return redirect(url_for("login",msg=msg))
    
@app.route('/send_message', methods=['POST'])
def send_message():
    email = session['email_patient']
    receiver = request.form.get('receiver')
    message = request.form.get('message')
    message_data = {
        'sender': email,
        'receiver': receiver,
        'message': message
    }
    db.messages.insert_one(message_data)
    return redirect('/chat/{}'.format(receiver))

@app.route('/send_message_doc', methods=['POST'])
def send_message_doc():
    email2 = session['email_doctor']
    receiver2 = request.form.get('receiver')
    message2 = request.form.get('message')
    message_data2 = {
        'sender': email2,
        'receiver': receiver2,
        'message': message2
    }
    db.messages.insert_one(message_data2)
    return redirect('/chat_doc/{}'.format(receiver2))

@app.route("/chat_doc/message_del", methods=['POST'])
def message_del():
    friend_del = request.form["friend_receive"]
    email = session["email_doctor"]
    friend = db.user_patient.find_one({'email': friend_del})
    db.messages.delete_many({
        '$or': [
            {'sender': email, 'receiver': friend['email']},
            {'sender': friend['email'], 'receiver': email}
        ]
    })
    return jsonify({'msg': 'Session Ended!'})

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)