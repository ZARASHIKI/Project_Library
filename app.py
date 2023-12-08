from dotenv import load_dotenv
import os
from os.path import join, dirname
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["UPLOAD_FOLDER"] = "./static/profile_pics"

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
app = Flask(__name__)

SECRET_KEY = 'ZARASHIKI'


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/collection', methods=['GET'])
def collection():
    return render_template('collection.html')

@app.route('/detail', methods=['GET'])
def detail():
    return render_template('detail.html')

@app.route('/bookmark', methods=['GET'])
def bookmark():
    return render_template('bookmark.html')
   
@app.route('/tambah', methods=['GET'])
def tambah():
    return render_template('tambah.html')
   
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)