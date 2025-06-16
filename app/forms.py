from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired, NumberRange
from wtforms import SelectField


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

class AddEmployeeForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    role = SelectField('Роль', choices=[('worker', 'Работник'), ('manager', 'Менеджер'), ('admin', 'Администратор')], default='worker')
    submit = SubmitField('Добавить')

class AddTaskForm(FlaskForm):
    time = FloatField('Время выполнения (часы)', validators=[DataRequired(), NumberRange(min=0)])
    correctness = FloatField('Процент выполнения', validators=[DataRequired(), NumberRange(min=0, max=100)])
    submit = SubmitField('Добавить задачу')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired()])
    new_password = PasswordField('Новый пароль', validators=[DataRequired()])
    submit = SubmitField('Сменить пароль')

class DeleteEmployeeForm(FlaskForm):
    submit = SubmitField('Удалить')