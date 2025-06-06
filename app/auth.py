from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.forms import LoginForm, AddEmployeeForm
from app.models import User, Employee

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

@bp.route('/employees', methods=['GET', 'POST'])
@login_required
def list_employees():
    if current_user.role != 'admin':
        flash("Доступ запрещен: требуется роль администратора.", 'error')
        return redirect(url_for('auth.login'))

    form = AddEmployeeForm()
    if form.validate_on_submit():
        employee = Employee(
            name=form.name.data,
            position=form.position.data,
            department=form.department.data,
            rating=form.rating.data,
            tasks=form.tasks.data,
            speed=form.speed.data,
            correctness=form.correctness.data,
            score=form.score.data
        )
        db.session.add(employee)
        db.session.commit()
        flash(f"Сотрудник {employee.name} добавлен.", 'info')
        return redirect(url_for('auth.list_employees'))

    employees = Employee.query.all()
    return render_template('employees.html', employees=employees, form=form)


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

@bp.route('/employees/edit/<int:emp_id>', methods=['GET', 'POST'])
@login_required
def edit_employee(emp_id):
    if current_user.role != 'admin':
        flash("Доступ запрещен.", 'error')
        return redirect(url_for('auth.list_employees'))
    emp = Employee.query.get_or_404(emp_id)
    form = AddEmployeeForm(obj=emp)
    if form.validate_on_submit():
        emp.name = form.name.data
        emp.position = form.position.data
        emp.department = form.department.data
        emp.rating = form.rating.data
        emp.tasks = form.tasks.data
        emp.speed = form.speed.data
        emp.correctness = form.correctness.data
        emp.score = form.score.data
        db.session.commit()
        flash(f"Данные сотрудника {emp.name} обновлены.", 'info')
        return redirect(url_for('auth.list_employees'))
    return render_template('edit_employee.html', form=form, emp=emp)