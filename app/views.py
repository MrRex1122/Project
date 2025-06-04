from flask import Blueprint, render_template, request, redirect, url_for,flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import pandas as pd
from app import db
from app.models import Employee
bp = Blueprint('views', __name__)
# Глобальная переменная для хранения текущих данных сотрудников
current_employees = [] # список объектов Employee или словарей с данными
# Вспомогательная функция для проверки расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}
 # Главная страница с таблицей и графиком
@bp.route('/')
@login_required
def dashboard():
    employees = Employee.query.all()
    num_employees = len(employees)
    all_tasks = [task for emp in employees for task in emp.tasks]
    num_tasks = len(all_tasks)
    total_time = sum(task.time for task in all_tasks) if all_tasks else 0
    avg_time = total_time / num_tasks if num_tasks else 0
    avg_correctness = sum(task.correctness for task in all_tasks) / num_tasks if num_tasks else 0
    avg_score = sum(emp.score() or 0 for emp in employees) / num_employees if num_employees else 0

    return render_template(
        'dashboard.html',
        employees=employees,
        num_employees=num_employees,
        num_tasks=num_tasks,
        total_time=total_time,
        avg_time=avg_time,
        avg_correctness=avg_correctness,
        avg_score=avg_score
    )



@bp.route('/reports')
@login_required
def reports():
    employees = Employee.query.all()
    # Сортировка по итоговому баллу по убыванию
    employees_sorted = sorted(employees, key=lambda e: e.score() or 0, reverse=True)
    names = [e.name for e in employees_sorted]
    departments = [e.department for e in employees_sorted]
    scores = [e.score() or 0 for e in employees_sorted]
    return render_template('reports.html', names=names, departments=departments, scores=scores)


@bp.route('/export_csv')
@login_required
def export_csv():
    employees = Employee.query.all()
    import csv
    from io import StringIO
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['ID', 'Имя', 'Отдел'])
    for e in employees:
        cw.writerow([e.id, e.name, getattr(e, 'department', '')])
    output = si.getvalue()
    return send_file(
        StringIO(output),
        mimetype='text/csv',
        as_attachment=True,
        download_name='employees.csv'
    )


@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_data():
    if request.method == 'POST':
        if current_user.role != 'admin':
            flash("У вас нет прав для загрузки данных.", 'error')
            return redirect(url_for('views.dashboard'))
        file = request.files.get('file')
        if not file or file.filename == '':
            flash("Файл не выбран.", 'error')
            return redirect(url_for('views.upload_data'))
        if allowed_file(file.filename):
            import pandas as pd
            df = pd.read_csv(file)
            # Определяем имена колонок
            if list(df.columns) == ['name', 'task_time', 'completion']:
                df.columns = ['name', 'time', 'correctness']
            elif list(df.columns) == ['name', 'time', 'correctness']:
                pass
            else:
                # Если нет заголовков, читаем без них
                df = pd.read_csv(file, header=None, names=['name', 'time', 'correctness'])
            # Очистить старые данные
            Task.query.delete()
            Employee.query.delete()
            db.session.commit()
            # Группируем задачи по сотруднику
            for name, group in df.groupby('name'):
                emp = Employee(name=name)
                db.session.add(emp)
                db.session.flush()  # чтобы получить emp.id
                for _, row in group.iterrows():
                    task = Task(employee_id=emp.id, time=row['time'], correctness=row['correctness'])
                    db.session.add(task)
            db.session.commit()
            flash("Данные успешно загружены и обработаны.", 'success')
            return redirect(url_for('views.dashboard'))
        else:
            flash("Недопустимый формат файла. Загрузите CSV.", 'error')
    return render_template('upload.html')