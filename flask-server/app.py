from flask import Flask, request, jsonify, make_response, abort
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import validates, relationship
from datetime import datetime
from sqlalchemy import ForeignKey
import pymysql
import json

app = Flask(__name__)
api = Api(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dldusdn1105@localhost:3306/intern_board'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# board model 
class Board(db.Model):
    __tablename__ = 'boards'
    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.String(2000), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(25), nullable=False)
    comments = relationship("Comment", back_populates="board")
    uploadedClock = db.Column(db.DateTime, nullable=False, default=datetime.utcnow().isoformat())
    
    def __init__(self, title, content, author, password, uploadClock):
        self.title = title
        self.content = content
        self.author = author
        self.password = password
        self.uploadClock = uploadClock
        
    def serializeForHome(self): # Board 직렬화 함수 ( 메인 페이지 )
        return {   
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "content": self.content,
            "comments": len(self.comments),
            "uploadedClock": self.uploadedClock.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] if self.uploadedClock else None
        }

        
    def serializeForDetail(self): # Board 직렬화 함수 ( 상세 페이지 )
        return {   
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "content": self.content,
            "comments":[comment.serialize() for comment in self.comments],
            "uploadedClock": self.uploadedClock.strftime('%Y-%m-%dT%H:%M:%S.%f') if self.uploadedClock else None
        }
        
    @classmethod # title 중복 확인 ( 게시글 업로드 )
    def is_duplicate_title(cls, title): 
        return bool(cls.query.filter_by(title=title).first())

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

    
    def __repr__(self): # title 반환
        return '<Board %r>' % self.title
    
    def serialize(self): # Comment 직렬화 함수 
        return {
            "id": self.id,
            "author": self.author,
            "content": self.content,
        }
    

@app.route('/posts', methods=['GET', 'POST']) # 추가, 목록 조회
def getjson():
    if request.method == 'GET': # 목록 조회 
        
        limit = request.args.get('limit', default=10, type=int)
        page = request.args.get('page', default=1, type=int)
        
        all_posts = Board.query.paginate(page=page, per_page=limit)
        posts = [post.serializeForHome() for post in all_posts.items]
        
        if not posts:
            return jsonify({"message": "아직 게시글이 없어요!"})

        result = {
            "posts": posts,
            "pageCount": all_posts.pages  # 전체 페이지 수
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
            title=data.get('title'),
            author=data.get('author'), 
            content=data.get('content'), 
            password=data.get('password'),
            uploadClock=datetime.utcnow()  # uploadClock는 현재 시간으로 설정
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
        
    if request.method == 'GET': # 상세페이지 불러오기 
        detail_posts = Board.query.get(board_id)
        serialized_post = detail_posts.serializeForDetail() # 직렬화된 포스트 가져오기 

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

            return jsonify({"post": post_info}) # post 반환
        else:
            return jsonify({"message": "게시글을 찾을 수 없습니다."}), 404 
        
    if request.method == 'POST':
        board = Board.query.filter_by(id=board_id).first()
        
        if not board: # 게시물이 없을 때 
            abort(404, description="게시물을 찾을 수 없습니다.")
            
        data = request.json  # 요청에서 JSON 데이터 가져오기
        params = ['content', 'author', 'password']
        
        for param in params:
            if param not in data:
                return make_response(jsonify("파라미터가 완전하지 않습니다"), 400)

        new_comment = Comment(
            content=data.get('content'),
            author=data.get('author'),
            password=data.get('password'),
            board_id=board_id
        )

        db.session.add(new_comment) # 댓글 추가
        db.session.commit() #커밋

        return jsonify({"commentId": new_comment.id}), 201
       
@app.route('/posts/<int:board_id>/comments/<comment_id>', methods=['DELETE']) # 코멘트 삭제
def deletecomm(board_id, comment_id):
    if request.method == 'DELETE': 
        password = request.args.get('password') # URL 파라미터 가져오기
        if not password:
            abort(400, description="비밀번호가 필요합니다.") 

        comment = Comment.query.get(comment_id)
        if not comment:
            abort(404, description="댓글을 찾을 수 없습니다.")
        
        board = Board.query.get(board_id)
        if not board:
            abort(404, description="게시물을 찾을 수 없습니다.")

        # 비밀번호 검사
        if board.password == password:  
            db.session.delete(comment)  # 댓글 삭제
            db.session.commit()  # 커밋
            return jsonify({"ok": True, "message": "댓글이 삭제되었습니다."}), 200
        else:
            return jsonify({"ok": False, "error": "비밀번호가 일치하지 않습니다."}), 403
            
    
if __name__ == "__main__":
    app.run(debug=True)