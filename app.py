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

SECRET_KEY = 'Libraryan'


@app.route('/', methods=['GET'])
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        collection = db.books_collection.find({},{'_id':False})
        for buku in collection:
            return render_template('index.html', user_info=user_info,books=buku)    
    except jwt.ExpiredSignatureError:
        collection = db.books_collection.find({},{'_id':False})
        for buku in collection:
            return render_template('index.html',books=buku)    
    except jwt.exceptions.DecodeError:
        collection = db.books_collection.find({},{'_id':False})
        for buku in collection:
            return render_template('index.html',books=buku)    

@app.route("/login")
def login():
    msg = request.args.get("msg")
    return render_template("login.html", msg=msg)

@app.route("/sign_in", methods=["POST"])
def sign_in():
    username_receive = request.form["username_give"]
    password_receive = request.form["password_give"]
    pw_hash = hashlib.sha256(password_receive.encode("utf-8")).hexdigest()
    result = db.user.find_one({"username": username_receive,"password": pw_hash,})
    if result:
        payload = {"id": username_receive,"exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),}
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return jsonify({"result": "success","token": token,})
    else:
        return jsonify({"result": "fail","msg": "We could not find a user with that id/password combination",})


@app.route("/sign_up/save", methods=["POST"])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                             
        "password": password_hash,                                  
        "profile_name": username_receive,
        "status":"pengunjung",                                                    
        "profile_pic": "", 
        "profile_pic_real": "profile/placeholder.png", 
        "profile_info": ""
    }
    db.user.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route("/sign_up/check_dup", methods=["POST"])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.user.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})


@app.route('/collection', methods=['GET'])
def collection():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]},{'_id': False})
        collection = db.books_collection.find({},{'_id':False})
        for buku in collection:
            return render_template('collection.html', user_info=user_info,books=buku)    
    except jwt.ExpiredSignatureError:
        collection = db.books_collection.find({},{'_id':False})
        for buku in collection:
            return render_template('collection.html',books=buku)    
    except jwt.exceptions.DecodeError:
        collection = db.books_collection.find({},{'_id':False})
        for buku in collection:
            return render_template('collection.html',books=buku)    
    
@app.route('/detail/<keyword>', methods=['GET'])
def detail(keyword):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]},{'_id': False})
        books_collection = db.books_collection.find_one({'Judul':keyword},{'_id':False})
        return render_template('detail.html',buku_detail=books_collection,user_info=user_info)
    except jwt.ExpiredSignatureError:
        books_collection = db.books_collection.find_one({'Judul':keyword},{'_id':False})
        return render_template('detail.html',buku_detail=books_collection)
    except jwt.exceptions.DecodeError:
        books_collection = db.books_collection.find_one({'Judul':keyword},{'_id':False})
        return render_template('detail.html',buku_detail=books_collection)

@app.route('/bookmark', methods=['GET'])
def bookmark():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        return render_template('bookmark.html', user_info=user_info)    
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="You Need To Login First"))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="You Need To Login First"))

@app.route("/tambah_buku/save", methods=["POST"])
def tambahBuku():
    judul_recieve = request.form['judul_give']
    penulis_recieve = request.form['penulis_give']
    genre_recieve = request.form['genre_give']
    link_recieve = request.form['link_give']
    deskirpsi_recieve = request.form['deskripsi_give']
    if "cover_give" in request.files:
        file = request.files["cover_give"]
        filename = secure_filename(file.filename)
        extension = filename.split(".")[-1]
        file_path = f"cover/{judul_recieve}.{extension}"
        file.save("./static/" + file_path)
    doc = {
        "Judul":judul_recieve,
        "Penulis":penulis_recieve,
        "Genre":genre_recieve,
        "Link":link_recieve,
        "Cover":file_path,
        "Deskripsi":deskirpsi_recieve
    }
    db.books_collection.insert_one(doc)
    return jsonify({'result': 'success','msg':'Book Added'})
   
if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)