# flask 패키지
from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import certifi
ca = certifi.where()
app = Flask(__name__)

from datetime import datetime

# mongoDB - pymongo, dnspython 패키지
from pymongo import MongoClient
import jwt
import datetime
import hashlib
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

# 몽고DB 연결
client = MongoClient('mongodb+srv://test:sparta@cluster0.m7jzf.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta


# 기본 메인 페이지 - 로그인페이지
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.Doglovers.find_one({"id": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))


@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('signup.html', msg=msg)


#로그인 포스트
@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    result = db.Doglovers.find_one({'id': username_receive, 'pw': pw_hash})

    if result is not None:
        payload = {
            'id': username_receive,
            'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'result': 'success', 'token': token})
        # 찾지 못하면
    else:
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
        'pw': pw_hash,
        'dog_breed': dog_breed_receive,
        'name': name_receive,
        'age': age_receive,
        'file': f'{filename}.{extension}',
        'time': f'{uploaddate}',
    }
    db.Doglovers.insert_one(doc)
    return jsonify({'msg': 'Saved'})


# 중복체크
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.Doglovers.find_one({"id": username_receive})) # true or false값을 뱉는다.
    return jsonify({'result': 'success', 'exists': exists}) # 그 결과값을 다시 client 로 보내준다.


#게시물 받아올 때 GET
@app.route('/upload', methods=['GET'])
def show_post():
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    # posts = list(db.upload.find({}, {'_id': False}))
    posts = list(db.upload.find({}).sort("date", -1).limit(20))
    for post in posts:
        post["_id"] = str(post["_id"])
        post["count_heart"] = db.likes.count_documents({"post_id": post["_id"], "type": "heart"})
        post["heart_by_me"] = bool(db.likes.find_one({"post_id": post["_id"], "type": "heart", "username": payload['id']}))
    return jsonify({'all_post': posts}, )

#게시물 업로드 할때 POST
@app.route('/upload', methods=['POST'])
def upload_file():
    #give데이터 받아오기
    comment_receive = request.form['comment_give']
    file = request.files["file_give"]

    #파일 이름을 지정하기 위한 작업
    extension = file.filename.split('.')[-1]
    today = datetime.now()
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    uploadtime=today.strftime('%m-%d %H:%M')
    filename= f'file-{mytime}'
    save_to = f'static/{filename}.jpg'
    file.save(save_to)

    #자유이용권 발급
    token_receive = request.cookies.get('mytoken')
    payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

    user_info = db.Doglovers.find_one({"id": payload["id"]})
    #DB에 데이터 저장
    doc={
        'profile' : user_info['file'],
        'username': user_info['id'],
        'userdog':user_info['dog_breed'],
        'age' : user_info['age'],
        'time':uploadtime,
        'comment':comment_receive,
        'file':f'{filename}.{extension}',
    }
    #upload라는 DB에 저장하기
    db.upload.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})

#좋아요 관련 함수 페이지
@app.route('/update_like', methods=['POST'])
def update_like():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 좋아요 수 변경
        user_info = db.Doglovers.find_one({"id": payload["id"]})
        post_id_receive = request.form["post_id_give"]
        type_receive = request.form["type_give"]
        action_receive = request.form["action_give"]
        doc = {
            "post_id": post_id_receive,
            "username": user_info['id'],
            "type": type_receive
        }
        if action_receive == "like":
            db.likes.insert_one(doc)
        else:
            db.likes.delete_one(doc)
        count = db.likes.count_documents({"post_id": post_id_receive, "type": type_receive})
        return jsonify({"result": "success", 'msg': 'updated', "count": count})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))




@app.route('/checkPost/<username>')
def check_post(username):
        # 각 사용자의 프로필과 글을 모아볼 수 있는 공간
        token_receive = request.cookies.get('mytoken')
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False
            user_info = db.upload.find_one({"username": username}, {"_id": False})
            print(user_info)
            return render_template('checkPost.html', user_info=user_info, status=status)
        except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
            return redirect(url_for("login"))


#각 사용자의 프로필을 볼 수 있는 페이지
@app.route('/user/<username>')
def user(username):
    token_receive = request.cookies.get('mytoken') #사용자정보를 받아주는 토큰입니다.
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])#사용자 정보를 받아줍니다
        status = (username == payload["id"])  # 내 프로필이면 True, 다른 사람 프로필 페이지면 False

        user_info = db.Doglovers.find_one({"id": username}, {"_id": False})
        return render_template('profile.html', user_info=user_info, status=status)
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


#프로필 수정 페이지(강의 뼈대입니다. 세화님이 수정부탁드립니다)
@app.route('/update_profile', methods=['POST'])
def save_img():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        username = payload["id"]
        name_receive = request.form["name_give"]
        about_receive = request.form["about_give"]
        new_doc = {
            "profile_name": name_receive,
            "profile_info": about_receive
        }
        if 'file_give' in request.files:
            file = request.files["file_give"]
            filename = secure_filename(file.filename)
            extension = filename.split(".")[-1]
            file_path = f"profile_pics/{username}.{extension}"
            file.save("./static/"+file_path)
            new_doc["profile_pic"] = filename
            new_doc["profile_pic_real"] = file_path
        db.users.update_one({'username': payload['id']}, {'$set':new_doc})
        return jsonify({"result": "success", 'msg': '프로필을 업데이트했습니다.'})
    except (jwt.ExpiredSignatureError, jwt.exceptions.DecodeError):
        return redirect(url_for("home"))


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)