from app import db
from passlib.apps import custom_app_context as pwd_context

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    def __init__(self, fullname, email, password):
        self.fullname = fullname
        self.email = email
        # Asumimos que la contraseña ya viene hasheada desde el registro
        self.password = password

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)
