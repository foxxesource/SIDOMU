from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
import certifi
ca = certifi.where()


app = Flask(__name__)
client = MongoClient('mongodb+srv://sriraihanputri:070502@cluster0.k5lmeah.mongodb.net/?retryWrites=true&w=majority', tlsCAFile = ca)
db = client.projectakhir

SECRET_KEY = "finalproject"

TOKEN_KEY= "mytoken"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route('/submit', methods=['POST'])
def submit():
    return redirect('/')

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)