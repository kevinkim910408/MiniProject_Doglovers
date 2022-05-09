# flask 패키지
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# mongoDB - pymongo, dnspython 패키지
from pymongo import MongoClient

# 몽고DB 연결
client = MongoClient('mongodb+srv://test:sparta@cluster0.m7jzf.mongodb.net/Cluster0?retryWrites=true&w=majority')
db = client.dbsparta


# 기본 메인 페이지 - index.html
@app.route('/')
def home():
    return render_template('index.html')






# 5000 포트 사용
if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)