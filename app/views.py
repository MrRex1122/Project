from flask import Blueprint, render_template, request, redirect, url_for,flash, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
import os
import pandas as pd
from app import db
from app.models import Employee, Task
bp = Blueprint('views', __name__)
from flask import Response
# Глобальная переменная для хранения текущих данных сотрудников
current_employees = [] # список объектов Employee или словарей с данными
# Вспомогательная функция для проверки расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'csv'}
 # Главная страница с таблицей и графиком
@bp.route('/')
@login_required
def dashboard():
    # Используем текущие загруженные данные о сотрудниках для отображения
    employees = current_employees
    return render_template('dashboard.html', employees=employees)
# Загрузка нового CSV-файла с данными сотрудников



@bp.route('/reports')
@login_required
def reports():
    employees = Employee.query.all()
    # Собираем пары (имя, балл)
    data = [(e.name, e.score() or 0) for e in employees]
    # Сортируем по баллу по убыванию
    data.sort(key=lambda x: x[1], reverse=True)
    names = [x[0] for x in data]
    scores = [x[1] for x in data]
    return render_template('reports.html', names=names, scores=scores)

@bp.route('/export_csv')
@login_required
def export_csv():
    employees = Employee.query.all()
    data = sorted([(e.name, e.score() or 0) for e in employees], key=lambda x: x[1], reverse=True)
    lines = ["name,score"]
    for name, score in data:
        lines.append(f"{name},{score}")
    # Добавляем BOM для корректного открытия в Excel
    csv_content = "\ufeff" + "\n".join(lines)
    return Response(
        csv_content,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment;filename=employee_scores.csv"}
    )



@bp.route('/upload', methods=['POST'])
@login_required
def upload_data():
    if current_user.role != 'admin':
        flash("У вас нет прав для загрузки данных.", 'error')
        return redirect(url_for('views.dashboard'))
    file = request.files.get('file')
    if not file or file.filename == '':
        flash("Файл не выбран.", 'error')
        return redirect(url_for('auth.list_employees'))
    if allowed_file(file.filename):
        import pandas as pd
        df = pd.read_csv(file)
        if list(df.columns) == ['name', 'task_time', 'completion']:
            df.columns = ['name', 'time', 'correctness']
        elif list(df.columns) == ['name', 'time', 'correctness']:
            pass
        else:
            df = pd.read_csv(file, header=None, names=['name', 'time', 'correctness'])
        Task.query.delete()
        Employee.query.delete()
        db.session.commit()
        for name, group in df.groupby('name'):
            emp = Employee(name=name)
            db.session.add(emp)
            db.session.flush()
            for _, row in group.iterrows():
                task = Task(employee_id=emp.id, time=row['time'], correctness=row['correctness'])
                db.session.add(task)
        db.session.commit()
        flash("Данные успешно загружены и обработаны.", 'success')
        return redirect(url_for('auth.list_employees'))
    else:
        flash("Недопустимый формат файла. Загрузите CSV.", 'error')
        return redirect(url_for('auth.list_employees'))