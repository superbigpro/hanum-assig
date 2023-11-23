from flask import Flask, redirect, request, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_restx import Api, Resource

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:dldusdn1105@127.0.0.1:5000/intern_board'  # 본인의 데이터베이스 URI로 바꿔주세요
db = SQLAlchemy(app)

class Board(db.Model):
    id = db.Column(db.Integer, primary_key=True, unique=True) # 고유 id
    title = db.Column(db.String(100), nullable=False, unique=True) # 제목
    content = db.Column(db.String(2000), nullable=False) # 게시글 내용 
    author = db.Column(db.String(20), nullable=False) # 작성자
    password = db.Column(db.String(25), nullable=False) # 작성자 비밀번호
    commentId = db.collumn(db.Interger, nullable=False) #
    comments = db.Column(db.Interger, nullable=False) # 댓글 갯수 (필수 X)
    addedDate = db.Column(db.String(30), nullable=False) # 생성 날짜 (필수 X)
    
def get_user_by_email(clock):
    return Board.query.filter_by(clock=clock).first()

@app.route('/posts', methods=['GET','POST'])
def getjson():
    if request.method == 'GET':
        data = {"dsa":"dsafgwWDFDWWDWD"}
        return jsonify(data)
    
    if request.method == 'POST':
        pass
        
if __name__ == "__main__":
    app.run(debug = True)
    