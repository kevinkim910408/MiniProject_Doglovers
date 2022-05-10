# flask 패키지
from flask import Flask, render_template, jsonify, request, session, redirect, url_for

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
client = MongoClient('mongodb+srv://test:sparta@cluster0.m7jzf.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta


# 기본 메인 페이지 - 로그인페이지
@app.route('/')
def home():
    return render_template('signup.html')

# 메인페이지 - 메인페이지
@app.route('/index')
def index():
    return render_template('index.html')

#로그인 포스트
@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()

    exists = bool(db.Doglovers.find_one({"id": username_receive},{"pw": password_receive})) # true or false값을 뱉는다.
    return jsonify({'result': 'success', 'exists': exists}) # 그 결과값을 다시 client 로 보내준다.

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


# 중복체크
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.Doglovers.find_one({"id": username_receive})) # true or false값을 뱉는다.
    return jsonify({'result': 'success', 'exists': exists}) # 그 결과값을 다시 client 로 보내준다.


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)