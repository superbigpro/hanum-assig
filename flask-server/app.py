from flask import Flask, request, jsonify, json, make_response, abort
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates, relationship
from datetime import datetime
from datetime import datetime
from sqlalchemy import ForeignKey
import pymysql

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dldusdn1105@localhost:3306/intern_board'

db = SQLAlchemy(app)

class Board(db.Model):
    __tablename__ = 'boards'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.String(2000), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(25), nullable=False)
    comments = relationship("Comment", back_populates="board")
    
    # comments = relationship("Comment", backref="board", lazy=True)  # comments 관계 추가
    
    def __init__(self, title, content, author, password, board_id):
        self.title = title
        self.content = content
        self.author = author
        self.password = password
        self.board_id = board_id
        
    def serializeForHome(self): # 직렬화 
        return {   
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "content": self.content,
            "comments": len(self.comments)
        }
        
    def serializeForDetail(self): # ''
        return {   
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "content": self.content,
            "comments":[comment.serialize() for comment in self.comments]
            
        }
    
# Comment 모델
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(500))
    author = db.Column(db.String(30))
    password = db.Column(db.String(30))
    board_id = db.Column(db.Integer, ForeignKey('boards.id'))  # Board 테이블의 id 열을 참조하는 외래 키
    board = relationship("Board", back_populates="comments")
    

    def __init__(self, content, author, password, board_id):  # board_id 추가
        self.content = content
        self.author = author
        self.password = password
        self.board_id = board_id

    
    def __repr__(self): # title return 
        return '<Board %r>' % self.title
    
    def serialize(self):
        return {
            "id": self.id,
            "author": self.author,
            "content": self.content,
        }
    
    @classmethod # title 중복 확인
    def is_duplicate_title(cls, title): 
        return bool(cls.query.filter_by(title=title).first())
    

@app.route('/posts', methods=['GET', 'POST']) # 추가, 목록 조회
def getjson():
    if request.method == 'GET': # 목록 조회 
        all_posts = Board.query.all()
        posts = [post.serializeForHome() for post in all_posts]

        result = {
            "posts": posts
        }

        return jsonify(result)

    if request.method == 'POST': # 글 추가 
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
            id=board_id
        )

        db.session.add(new_board)  # 새로운 데이터 추가
        db.session.commit()  # 커밋

        result = { # 반환할 json 
            "postId": new_board.id
        }

        return make_response(jsonify(result), 200)
    
@app.route('/posts/<int:board_id>', methods=['GET', 'DELETE']) # 삭제, 상세 페이지
def removepost(board_id):
    if request.method == 'DELETE':
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
        
    if request.method == 'GET':
        detail_posts = Board.query.get(board_id)
        serialized_post = detail_posts.serializeForDetail()

        result = {
            "posts": serialized_post
        }

        return jsonify(result)

@app.route('/posts/<int:board_id>/comments', methods=['GET', 'POST']) # 댓글 
def reple(board_id):
    if request.method == 'GET':
        board = Board.query.filter_by(id=board_id).first()    
        
        if board:
            # 게시글 정보 가져오기
            post_info = {
                "id": board.id,
                "title": board.title,
                "author": board.author,
                "content": board.content,
                "comments": [] 
            }

            # 해당 게시글에 대한 댓글 가져오기
            for comment in board.comments:
                comment_info = {
                    "id": comment.id,
                    "author": comment.author,
                    "content": comment.content,
                    "uploadedAt": comment.uploaded_at.strftime("%Y-%m-%dT%H:%M:%S")  # 날짜 포맷 변경
                }
                post_info["comments"].append(comment_info)  # 댓글 정보를 게시글 정보에 추가

            return jsonify({"post": post_info})
        else:
            return jsonify({"message": "게시글을 찾을 수 없습니다."}), 404
        
    if request.method == 'POST':
        board = Board.query.filter_by(id=board_id).first()
        
        if not board: # 게시물이 없을 때 
            abort(404, description="게시물을 찾을 수 없습니다.")
        
        data = request.json  # 요청에서 JSON 데이터 가져오기
        
        expected_params = ['content', 'author', 'password']

        for param in expected_params:
            if param not in data:
                return make_response(jsonify("파라미터가 완전하지 않습니다"), 400)
                
        new_comment = Comment(
            content=data['content'],
            author=data['author'],
            password=data['password'],
            board_id=board_id
        )

        db.session.add(new_comment)
        db.session.commit()

        return jsonify({"commentId": new_comment.id}), 201
       
    
if __name__ == "__main__":
    app.run(debug=True)