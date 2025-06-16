from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.forms import LoginForm, AddEmployeeForm, AddTaskForm
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
    if current_user.role != 'admin':
        flash("Доступ запрещен: требуется роль администратора.", 'error')
        return redirect(url_for('auth.login'))

    employees = Employee.query.all()
    return render_template('employees.html', employees=employees)


@bp.route('/employees/delete/<int:emp_id>', methods=['POST'])
@login_required
def delete_employee(emp_id):
    if current_user.role != 'admin':
        flash("Доступ запрещен.", 'error')
        return redirect(url_for('auth.list_employees'))
    emp = Employee.query.get_or_404(emp_id)
    db.session.delete(emp)
    db.session.commit()
    flash(f"Сотрудник {emp.name} удалён.", 'info')
    return redirect(url_for('auth.list_employees'))

@bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    if current_user.role != 'admin':
        flash("Доступ запрещен.", 'error')
        return redirect(url_for('auth.list_employees'))
    form = AddEmployeeForm()
    if form.validate_on_submit():
        emp = Employee(
            name=form.name.data,
            position=form.position.data,
            department=form.department.data,
            rating=form.rating.data
        )
        db.session.add(emp)
        db.session.commit()
        flash(f"Сотрудник {emp.name} добавлен.", 'success')
        return redirect(url_for('auth.list_employees'))
    return render_template('add_employee.html', form=form)

@bp.route('/employees/<int:emp_id>/add_task', methods=['GET', 'POST'])
@login_required
def add_task(emp_id):
    if current_user.role != 'admin':
        flash("Доступ запрещен.", 'error')
        return redirect(url_for('auth.list_employees'))
    emp = Employee.query.get_or_404(emp_id)
    form = AddTaskForm()
    if form.validate_on_submit():
        task = Task(employee_id=emp.id, time=form.time.data, correctness=form.correctness.data)
        db.session.add(task)
        db.session.commit()
        flash("Задача добавлена.", 'success')
        return redirect(url_for('auth.list_employees'))
    return render_template('add_task.html', form=form, employee=emp)