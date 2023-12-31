import math
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

SECRET_KEY = 'Libraryan'


@app.route('/', methods=['GET'])
def home():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        collection = db.books_collection.find({},{'_id':False}).limit(9)
        list_buku=list(collection)
        return render_template('index.html', user_info=user_info,books=list_buku)    
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        collection = db.books_collection.find({},{'_id':False}).limit(9)
        list_buku=list(collection)
        return render_template('index.html',books=list_buku)       

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
        "profile_pic_real": "profile/placeholder.svg", 
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
        page = request.args.get('page', default=1, type=int)
        per_page = 6
        offset = (page - 1) * per_page
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]},{'_id': False})
        total_books = db.books_collection.count_documents({})
        total_pages = math.ceil(total_books / per_page)
        collection = list(db.books_collection.find({},{'_id':False}).skip(offset).limit(per_page))
        return render_template('collection.html', user_info=user_info,books=collection,current_page=page,total_pages=total_pages)    
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        collection = db.books_collection.find({},{'_id':False})
        total_books = db.books_collection.count_documents({})
        total_pages = math.ceil(total_books / per_page)
        collection = list(db.books_collection.find({},{'_id':False}).skip(offset).limit(per_page))
        return render_template('collection.html',books=collection,current_page=page,total_pages=total_pages)    
    
@app.route('/detail/<keyword>', methods=['GET'])
def detail(keyword):
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]},{'_id': False})
        books_collection = db.books_collection.find_one({'Judul':keyword})
        if 'Genre' in books_collection:
            genre_to_search = books_collection['Genre']
            discovery = db.books_collection.find({"Genre": {"$all":genre_to_search}})
            return render_template('detail.html',buku_detail=books_collection,user_info=user_info,discovery=discovery)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        books_collection = db.books_collection.find_one({'Judul':keyword})
        genre = 'Genre'
        if genre in books_collection:
            genre_to_search = books_collection['Genre']
            discovery = db.books_collection.find({"Genre": {"$all":genre_to_search}})
            return render_template('detail.html',buku_detail=books_collection,user_info='',discovery=discovery)


@app.route('/bookmark/add', methods=['POST'])
def bookmarkadd():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        cover_receive = request.form["cover_give"]
        detail_receive = request.form["detail_give"]
        type_receive = request.form["type_give"]
        id_receive = request.form["id_give"]
        judul_receive = request.form["judul_give"]
        cek_dup = db.bookmark.find_one({"judul": judul_receive, "username": user_info["profile_name"]})
        if cek_dup:
            db.bookmark.delete_one(cek_dup)
        else:
            doc = {
                "bookmark_id": id_receive,
                "type": type_receive,
                "cover": cover_receive,
                "username": user_info['profile_name'],
                "detail": detail_receive,
                "judul": judul_receive
            }
            db.bookmark.insert_one(doc)

        return jsonify({"result": "success"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login"))


@app.route('/bookmark/cek', methods=['GET'])
def bookmarkget():
    token_receive = request.cookies.get("mytoken")
    try:    
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username_receive = request.args.get("username_give")
        if username_receive == "":
            bookmark_get = "No Have Bookmark"
        else:
            bookmark_get = list(db.bookmark.find({"username":username_receive}))

        for bookmark in bookmark_get:
            bookmark["_id"] = str(bookmark["_id"])
            bookmark["bookmark_me"] = bool(
                db.bookmark.find_one(
                    {"bookmark_id": bookmark["bookmark_id"], "type": "bookmark", "username": payload["id"]}
                )
            )
        return jsonify({"result": "success","msg": "Successful fetched all posts","bookmark": bookmark_get})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="You Need To Login First"))

    
@app.route('/bookmark', methods=['GET'])
def bookmark():
    token_receive = request.cookies.get("mytoken")
    try:    
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        page = request.args.get('page', default=1, type=int)
        per_page = 9
        offset = (page - 1) * per_page
        total_books = db.bookmark.count_documents({})
        total_pages = math.ceil(total_books / per_page)
        bookmark_get = list(db.bookmark.find({"username":user_info["profile_name"]}).skip(offset).limit(per_page))

        for bookmark in bookmark_get:
            bookmark["_id"] = str(bookmark["_id"])
            bookmark["bookmark_me"] = bool(
                db.bookmark.find_one(
                    {"bookmark_id": bookmark["bookmark_id"], "type": "bookmark", "username": payload["id"]}
                )
            )
        return render_template('bookmark.html', user_info=user_info,bookmark=bookmark_get,current_page=page,total_pages=total_pages)    
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="You Need To Login First"))

@app.route("/tambah_buku/save", methods=["POST"])
def tambahBuku():
    judul_recieve = request.form['judul_give']
    penulis_recieve = request.form['penulis_give']
    genre_recieve = request.form['genre_give']
    genres = [genre.strip() for genre in genre_recieve.split(',')]
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
        "Genre":genres,
        "Link":link_recieve,
        "Cover":file_path,
        "Deskripsi":deskirpsi_recieve
    }
    db.books_collection.insert_one(doc)
    return jsonify({'result': 'success','msg':'Book Added'})

@app.route("/Edit_buku/save", methods=["POST"])
def Edit_buku():
    judul_recieve = request.form['judul_give']
    penulis_recieve = request.form['penulis_give']
    genre_recieve = request.form['genre_give']
    genres = [genre.strip() for genre in genre_recieve.split(',')]
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
        "Genre":genres,
        "Link":link_recieve,
        "Cover":file_path,
        "Deskripsi":deskirpsi_recieve
    }
    db.books_collection.update_one({'Judul':judul_recieve},{"$set":doc})
    return jsonify({'result': 'success','msg':'Book Updated'})
    
@app.route("/delete_buku/save", methods=["POST"])
def delete_buku():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]})
        judul_receive = request.form['judul_give']
        db.bookmark.delete_many({"username":user_info['profile_name']})
        db.books_collection.delete_one({'Judul':judul_receive})
        return jsonify({'result': 'success','msg':'Book Deleted'})    
    except (jwt.ExpiredSignatureError,jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="You Need To Login First"))
    
   
@app.route("/update_profile", methods=["POST"])
def update_profile():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        username = payload["id"]
        name_receive = request.form["name_give"]
        new_doc = {"profile_name": name_receive,}
        if "file_give" in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile/{username}.{extension}"
            file.save("./static/" + file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.user.update_one({"username": payload["id"]}, {"$set": new_doc})
        return jsonify({"result": "success", "msg": "Profile updated!"})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="You Need To Login First"))

@app.route("/profile", methods=["GET"])
def profilePage():
    token_receive = request.cookies.get("mytoken")
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=["HS256"])
        user_info = db.user.find_one({"username": payload["id"]},{'_id': False})
        count = db.bookmark.count_documents({"username": user_info['profile_name']})
        return render_template('profile.html',user_info=user_info,count=count)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("login", msg="You Need To Login First"))

if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)