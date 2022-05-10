# flask 패키지
from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from datetime import datetime

# mongoDB - pymongo, dnspython 패키지
from pymongo import MongoClient

SECRET_KEY = 'SPARTA'

import jwt

import hashlib

# 몽고DB 연결
client = MongoClient('mongodb+srv://test:sparta@cluster0.m7jzf.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta


# 기본 메인 페이지 - index.html
@app.route('/')
def home():
    return render_template('index.html')


# 로그인 페이지 - login.html
@app.route('/login')
def login():
    return render_template('login.html')



# 회원가입 페이지 - signup.html
@app.route('/signup')
def signup():
    return render_template('signup.html')


# 로그인 포스트
@app.route("/login", methods=["POST"])
def login_post():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    result = db.Doglovers.find_one({'id': id_receive, 'pw': pw_hash})
    return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})


# 회원가입 포스트
@app.route('/signup/save', methods=['POST'])
def signup_post():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    dog_breed_receive = request.form['dog_breed_give']
    name_receive = request.form['name_give']
    age_receive = request.form['age_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    # file을 보낼 준비
    file = request.files["file_give"]
    extension = file.filename.split('.')[-1]

    # 현재시간을 가져오는 함수
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    uploaddate = today.strftime('%Y-%m-%d')

    # 파일의 이름은 file-현재시간을 붙힌다
    filename = f'file-{mytime}'

    # 파일의 경로
    save_to = f'static/{filename}.{extension}'

    # 내가 save_to 라는 파일을 저장할거다
    file.save(save_to)

    doc = {
        'id': id_receive,
        'pw': pw_receive,
        'dog_breed': dog_breed_receive,
        'name': name_receive,
        'age': age_receive,
        'file': f'{filename}.{extension}',
        'time': f'{uploaddate}',
    }

    db.Doglovers.insert_one(doc)
    return jsonify({'msg': 'Saved'})

@app.route('/signup/check_dup', methods=['POST'])
def check_dup():
    id_receive = request.form['id_give']
    exists = bool(db.Doglovers.find_one({"id": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})


# 5000 포트 사용
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
