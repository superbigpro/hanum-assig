from flask import Flask, redirect, request, json, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
db = SQLAlchemy()

class Timetable(db.Model):
    id = db.Column(db.Integer, primary_key=True) # 고유 id
    clock = db.Column(db.String(10), nullable=False) # 시간
    time = db.Column(db.String(10), nullable=False) # 교시 
    content = db.Column(db.String(10), nullable=False) # 교과목 
    
def get_user_by_email(clock):
    return Timetable.query.filter_by(clock=clock).first()

@app.route('/posts', methods=['GET','POST'])
def getjson():
    if request.method == 'GET':
        data = {"dsa":"dsafgwWDFDWWDWD"}
        return jsonify(data)
    
    

if __name__ == "__main__":
    app.run(debug = True)
    