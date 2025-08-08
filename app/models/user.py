from app import db
from passlib.hash import pbkdf2_sha256 as sha256

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, fullname, email, password):
        self.fullname = fullname
        self.email = email
        self.password = sha256.hash(password)

    def verify_password(self, password):
        return sha256.verify(password, self.password)