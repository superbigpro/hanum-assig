from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:dldusdn1105@127.0.0.1:5000/intern_board'
db = SQLAlchemy(app)

class Board(db.Model):
    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    title = db.Column(db.String(100), nullable=False, unique=True)
    content = db.Column(db.String(2000), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(25), nullable=False)
    commentId = db.Column(db.Integer, nullable=False)
    comments = db.Column(db.Integer, nullable=False)
    addedDate = db.Column(db.String(30), nullable=False)

    def __init__(self, title, content, author, password, commentId, comments, addedDate):
        self.title = title
        self.content = content
        self.author = author
        self.password = password
        self.commentId = commentId
        self.comments = comments
        self.addedDate = addedDate

def get_user_by_email(clock):
    return Board.query.filter_by(clock=clock).first()

@app.route('/posts', methods=['GET', 'POST'])
def getjson():
    if request.method == 'GET':
        data = {"dsa": "dsafgwWDFDWWDWD"}
        return jsonify(data)

    if request.method == 'POST':
        pass

if __name__ == "__main__":
    app.run(debug=True)
