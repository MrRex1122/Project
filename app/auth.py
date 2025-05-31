from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app import db
from app.forms import LoginForm, AddUserForm

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('views.dashboard'))
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            flash("Неправильные имя пользователя или пароль", 'error')
        else:
            login_user(user)
            return redirect(url_for('views.dashboard'))
    return render_template('login.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

# Управление пользователями и сотрудниками (только для администратора)
@bp.route('/users', methods=['GET', 'POST'])
@login_required
def list_users():
    if current_user.role != 'admin':
        flash("Доступ запрещен: требуется роль администратора.", 'error')
        return redirect(url_for('views.dashboard'))

    user_form = AddUserForm()

    if user_form.validate_on_submit():
        username = user_form.username.data
        password = user_form.password.data
        role = user_form.role.data or 'user'
        department = user_form.department.data
        rating = user_form.rating.data
        if User.query.filter_by(username=username).first():
            flash("Пользователь с таким именем уже существует.", 'error')
        else:
            new_user = User(
                username=username,
                role=role,
                # добавьте department и rating в модель User, если нужно
            )
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash(f"Пользователь {username} создан.", 'info')
        return redirect(url_for('auth.list_users'))

    users = User.query.all()
    return render_template(
        'users.html',
        users=users,
        user_form=user_form
    )