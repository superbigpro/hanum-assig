from flask import Flask, request, jsonify, json, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
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
    # commentId = db.Column(db.Integer, nullable=False) # 선 
    # comments = db.Column(db.Integer, nullable=False) #  택 
    # addedDate = db.Column(db.String(30), nullable=False)# 기능

    def __init__(self, title, content, author, password): # init 생성 (보류 : , commentId, comments, addedDate)
        self.title = title
        self.content = content
        self.author = author
        self.password = password
        # self.commentId = commentId
        # self.comments = comments
        # self.addedDate = addedDate
        
    def serializeForHome(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            # "uploadAt": self.uploadAt.isoformat()
        }
        
    def serializeForDetail(self):
        return {   
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "content": self.content, 
        }
    
    def __repr__(self): # title return 
        return '<Board %r>' % self.title
    
    @classmethod
    def is_duplicate_title(cls, title):
        return bool(cls.query.filter_by(title=title).first())



@app.route('/posts', methods=['GET', 'POST'])
def getjson():
    if request.method == 'GET': # 테스트 코드 (작동함)
        all_posts = Board.query.all()
        posts = [post.serializeForHome() for post in all_posts]

        result = {
            "posts": posts
        }

        return jsonify(result)

    if request.method == 'POST':
        data = request.json  # 요청에서 JSON 데이터 가져오기

        # 파라미터가 비어있는지 확인 
        params = ['title', 'content', 'author', 'password']
        for param in params:
            if param not in data:
                return make_response(jsonify('파라미터가 완전하지 않습니다.'), 400)
            
        # 파라미터가 중복인지 확인 
        title = data['title']
        if Board.is_duplicate_title(title):
            return make_response(jsonify('중복된 제목입니다.'), 409)
        
        # Validator 추가 예정 

        new_board = Board(
            title=data['title'],
            author=data.get('author'), 
            content=data['content'], 
            password=data.get('password'),  
            # commentId=data.get('commentId', 0),  # 선택기능
            # comments=data.get('comments', 0),  # '' 
            # addedDate=datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # '' , iso 포맷으로 처리 
        )

        db.session.add(new_board)  # 새로운 데이터 추가
        db.session.commit()  # 커밋

        result = { # 반환할 json 
            "postId": new_board.id
        }

        return make_response(jsonify(result), 200)
    
@app.route('/posts/<int:board_id>', methods=['POST'])
def removepost(board_id):
    if request.method == 'POST':
        password = request.args.get("password")  # URL에서 password 파라미터 가져오기

        board = Board.query.get(board_id)  # 게시물 조회

        if board is None:
            return jsonify({"error": "게시물을 찾을 수 없습니다."}), 404

        if board.password == password:  # 비밀번호 일치 여부 확인
            db.session.delete(board)  # 게시물 삭제
            db.session.commit() # 커밋 
            return jsonify({"ok": True, "message": "게시물이 삭제되었습니다."}), 200 
        else:
            return jsonify({"ok": False, "error": "비밀번호가 일치하지 않습니다."}), 403

if __name__ == "__main__":
    app.run(debug=True)