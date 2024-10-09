from app import db

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(6), unique=True, nullable=False)
    student_count = db.Column(db.Integer, default=0)

class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(6), db.ForeignKey('room.code'), nullable=False)
    good_count = db.Column(db.Integer, default=0)
    neutral_count = db.Column(db.Integer, default=0)
    bad_count = db.Column(db.Integer, default=0)
