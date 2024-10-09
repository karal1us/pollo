import os
import random
import string
import qrcode
import io
import base64
import time
from PIL import Image, ImageDraw
from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from threading import Timer

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("FLASK_SECRET_KEY") or "a secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///polling_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

socketio = SocketIO(app)

from models import Room, Poll

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def generate_qr_code(room_code):
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(f"http://localhost:5000/join/{room_code}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img_buffer = io.BytesIO()
    img.save(img_buffer, format="PNG")
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_room', methods=['POST'])
def create_room():
    room_code = generate_room_code()
    qr_code = generate_qr_code(room_code)
    new_room = Room(code=room_code)
    db.session.add(new_room)
    db.session.commit()
    session['room'] = room_code
    session['is_teacher'] = True
    return render_template('teacher.html', room_code=room_code, qr_code=qr_code)

@app.route('/join/<room_code>')
def join(room_code):
    room = Room.query.filter_by(code=room_code).first()
    if room:
        session['room'] = room_code
        session['is_teacher'] = False
        return render_template('student.html', room_code=room_code)
    return "Room not found", 404

@socketio.on('join')
def on_join(data):
    room = data['room']
    join_room(room)
    if not session.get('is_teacher'):
        room_obj = Room.query.filter_by(code=room).first()
        if room_obj:
            room_obj.student_count += 1
            db.session.commit()
            emit('update_student_count', {'count': room_obj.student_count}, room=room)

@socketio.on('leave')
def on_leave(data):
    room = data['room']
    leave_room(room)
    if not session.get('is_teacher'):
        room_obj = Room.query.filter_by(code=room).first()
        if room_obj and room_obj.student_count > 0:
            room_obj.student_count -= 1
            db.session.commit()
            emit('update_student_count', {'count': room_obj.student_count}, room=room)

@socketio.on('send_poll')
def send_poll(data):
    room = data['room']
    new_poll = Poll(room_code=room)
    db.session.add(new_poll)
    db.session.commit()
    emit('new_poll', {'poll_id': new_poll.id}, room=room)
    
    # Start countdown timer
    countdown_timer(room, new_poll.id, 30)

def countdown_timer(room, poll_id, duration):
    for i in range(duration, 0, -1):
        socketio.emit('update_countdown', {'seconds': i}, room=room)
        socketio.sleep(1)
    clear_poll(room, poll_id)

def clear_poll(room, poll_id):
    with app.app_context():
        poll = Poll.query.get(poll_id)
        if poll:
            db.session.delete(poll)
            db.session.commit()
        socketio.emit('clear_poll', room=room)

@socketio.on('submit_answer')
def submit_answer(data):
    poll_id = data['poll_id']
    answer = data['answer']
    poll = Poll.query.get(poll_id)
    if poll:
        if answer == 'good':
            poll.good_count += 1
        elif answer == '50/50':
            poll.neutral_count += 1
        elif answer == 'bad':
            poll.bad_count += 1
        db.session.commit()
        emit('update_results', {
            'good': poll.good_count,
            'neutral': poll.neutral_count,
            'bad': poll.bad_count
        }, room=poll.room_code)

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)
