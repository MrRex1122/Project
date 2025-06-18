from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.forms import LoginForm, AddEmployeeForm, AddTaskForm, ChangePasswordForm, DeleteEmployeeForm
from app.models import User, Employee, Task

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



@bp.route('/employees', methods=['GET'])
@login_required
def list_employees():
    employees = Employee.query.all()
    delete_form = DeleteEmployeeForm()
    return render_template('employees.html', employees=employees, delete_form=delete_form)

@bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if current_user.role != 'admin':
        flash("Доступ разрешен только администратору.", 'error')
        return redirect(url_for('auth.list_employees'))
    form = AddEmployeeForm()
    if form.validate_on_submit():
        emp = Employee(
            name=form.name.data
        )
        db.session.add(emp)
        db.session.commit()
        # Создать пользователя для входа (username = name)
        user = User(username=form.name.data, role=form.role.data)
        user.set_password('password')  # пароль по умолчанию
        db.session.add(user)
        db.session.commit()
        flash(f"Сотрудник {emp.name} и пользователь {user.username} добавлены.", 'success')
        return redirect(url_for('auth.list_employees'))
    return render_template('add_employee.html', form=form)

@bp.route('/employees/delete/<int:emp_id>', methods=['POST'])
@login_required
def delete_employee(emp_id):
    if current_user.role != 'admin':
        flash("Удаление разрешено только администратору.", 'error')
        return redirect(url_for('auth.list_employees'))
    emp = Employee.query.get_or_404(emp_id)
    # Удаляем связанного пользователя
    user = User.query.filter_by(username=emp.name).first()
    if user:
        db.session.delete(user)
    db.session.delete(emp)
    db.session.commit()
    flash(f"Сотрудник {emp.name} удалён.", 'info')
    return redirect(url_for('auth.list_employees'))

@bp.route('/employees/<int:emp_id>/add_task', methods=['GET', 'POST'])
@login_required
def add_task(emp_id):
    # Работник может добавлять задачи только себе
    if current_user.role == 'worker':
        emp = Employee.query.filter_by(id=emp_id, name=current_user.username).first()
        if not emp:
            flash("Вы можете добавлять задачи только себе.", 'error')
            return redirect(url_for('views.dashboard'))
    elif current_user.role in ['admin', 'manager']:
        emp = Employee.query.get_or_404(emp_id)
    else:
        flash("Доступ запрещен.", 'error')
        return redirect(url_for('views.dashboard'))

    form = AddTaskForm()
    if form.validate_on_submit():
        task = Task(employee_id=emp.id, time=form.time.data, correctness=form.correctness.data)
        db.session.add(task)
        db.session.commit()
        flash("Задача добавлена.", 'success')
        return redirect(url_for('auth.list_employees'))
    return render_template('add_task.html', form=form, employee=emp)


@bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.old_password.data):
            flash('Старый пароль неверен.', 'error')
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Пароль успешно изменён.', 'success')
            return redirect(url_for('views.dashboard'))
    return render_template('change_password.html', form=form)