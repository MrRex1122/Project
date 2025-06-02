from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='admin')
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    time = db.Column(db.Float)
    correctness = db.Column(db.Float)

    employee = db.relationship('Employee', back_populates='tasks')

class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    position = db.Column(db.String(100))
    department = db.Column(db.String(100))
    rating = db.Column(db.Float)
    tasks = db.relationship('Task', back_populates='employee', cascade='all, delete-orphan')

    def tasks_count(self):
        return len(self.tasks)

    def avg_time(self):
        if not self.tasks:
            return 0
        return sum(t.time for t in self.tasks) / len(self.tasks)

    def avg_correctness(self):
        if not self.tasks:
            return 0
        return sum(t.correctness for t in self.tasks) / len(self.tasks)

    def score(self):
        n = self.tasks_count()
        # Критерий 1: количество задач
        if n >= 10:
            w1 = 0.5
        elif 5 <= n <= 9:
            w1 = 0.3
        else:
            w1 = 0.2

        # Критерий 2: среднее время
        avg_time = self.avg_time()
        if avg_time <= 2:
            w2 = 0.5
        elif 2 < avg_time <= 5:
            w2 = 0.3
        else:
            w2 = 0.2

        # Критерий 3: средний % выполнения
        avg_corr = self.avg_correctness()
        if 85 <= avg_corr <= 100:
            w3 = 0.6
        elif 50 <= avg_corr < 85:
            w3 = 0.3
        else:
            w3 = 0.1

        # Итоговый балл
        return round(w1 * 0.45 + w2 * 0.3 + w3 * 0.25, 2)

