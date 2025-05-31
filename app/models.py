from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='user')
    department = db.Column(db.String(100))
    rating = db.Column(db.Float)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def __repr__(self):
        return f'<User {self.username}>'
# Опционально, модель для сотрудников (если нужно сохранять историю или сложные фильтры)
class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    position = db.Column(db.String(100))      # новая строка
    department = db.Column(db.String(100))    # новая строка
    rating = db.Column(db.Float)              # новая строка
    tasks = db.Column(db.Integer)
    speed = db.Column(db.Float)
    correctness = db.Column(db.Float)
    score = db.Column(db.Float)
    def __repr__(self):
        return f'<Employee {self.name} score={self.score}>'