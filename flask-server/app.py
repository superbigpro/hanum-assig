from flask import Flask, request, jsonify, json, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pymysql

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dldusdn1105@localhost:3306/intern_board'
# 기존의 import 및 설정 부분

db = SQLAlchemy(app)

class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.String(2000), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(25), nullable=False)
    # commentId = db.Column(db.Integer, nullable=False)
    # comments = db.Column(db.Integer, nullable=False)
    # addedDate = db.Column(db.String(30), nullable=False)

    def __init__(self, title, content, author, password, commentId, comments, addedDate):
        self.title = title
        self.content = content
        self.author = author
        self.password = password
        # self.commentId = commentId
        # self.comments = comments
        # self.addedDate = addedDate
    
    def __repr__(self):
        return '<Board %r>' % self.title


@app.route('/posts', methods=['GET', 'POST'])
def getjson():
    if request.method == 'GET': # 테스트 코드 (작동함)
        data = {"dsa": "dsafgwWDFDWWDWD"}
        return jsonify(data)

    if request.method == 'POST':
        data = request.json  # 요청에서 JSON 데이터 가져오기

        # 요청에 필요한 파라미터가 있는지 확인
        params = ['title', 'content', 'author', 'password']
        for param in params:
            if param not in data:
                return make_response(jsonify('파라미터가 완전하지 않습니다.'), 400)

        new_board = Board(
            title=data['title'],
            content=data['content'],
            author=data.get('author', ''),  
            password=data.get('password', ''),  
            # commentId=data.get('commentId', 0),  # 선택기능
            # comments=data.get('comments', 0),  # '' 
            # addedDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # '' , iso 포맷으로 처리 
        )

        db.session.add(new_board)  # 새로운 데이터 추가
        db.session.commit()  # 커밋

        result = { # 반환할 json 
            "result": "OK"
        }

        return make_response(jsonify(result), 200)

if __name__ == "__main__":
    app.run(debug=True)
