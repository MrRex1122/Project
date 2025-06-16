from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, NumberRange


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')




class AddEmployeeForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    position = StringField('Должность', validators=[DataRequired()])
    department = StringField('Отдел')
    rating = FloatField('Рейтинг')
    tasks = IntegerField('Задачи')
    speed = FloatField('Скорость')
    correctness = FloatField('Точность')
    score = FloatField('Итоговый балл')
    submit = SubmitField('Добавить')


class AddTaskForm(FlaskForm):
    time = FloatField('Время выполнения (часы)', validators=[DataRequired(), NumberRange(min=0)])
    correctness = FloatField('Процент выполнения', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Добавить задачу')