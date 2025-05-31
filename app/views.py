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
    # Используем текущие загруженные данные о сотрудниках для отображения
    employees = current_employees
    return render_template('dashboard.html', employees=employees)
# Загрузка нового CSV-файла с данными сотрудников
@bp.route('/employees/add', methods=['POST'])
@login_required
def add_employee():
    if current_user.role != 'admin':
        return "Forbidden", 403
    name = request.form.get('name')
    email = request.form.get('email')
    role = request.form.get('role')
    if not name or not role:
        flash("Имя и должность обязательны.", 'error')
        return redirect(url_for('auth.list_users'))
    from app.models import Employee
    new_employee = Employee(name=name, tasks=0, speed=0, correctness=0, score=0)
    db.session.add(new_employee)
    db.session.commit()
    flash(f"Сотрудник {name} добавлен.", 'info')
    return redirect(url_for('auth.list_users'))
@bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_data():
    if request.method == 'POST':
        # Только администратор может загружать новые данные
        if current_user.role != 'admin':
            flash("У вас нет прав для загрузки данных.", 'error')
            return redirect(url_for('views.dashboard'))
            file = request.files.get('file')
        if not file or file.filename == '':
            flash("Файл не выбран.", 'error')
            return redirect(url_for('views.upload_data'))
        if allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(os.getcwd(), 'data', filename)
            file.save(filepath)
            flash(f"Файл {filename} загружен. Выполняется расчет эффективности...", 'info')
            # Чтение CSV и расчет показателей
            data = pd.read_csv(filepath)
            # Предполагаем, что CSV содержит колонки: Name, Tasks, Speed, Correctness
            if 'Name' in data.columns:
                data.rename(columns={'Name': 'name', 'Tasks': 'tasks','Speed': 'speed', 'Correctness':'correctness'}, inplace=True)
            # Приводим числовые столбцы к float
            data['tasks'] = data['tasks'].astype(float)
            data['speed'] = data['speed'].astype(float)
            data['correctness'] = data['correctness'].astype(float)
            # Нормировка и расчет интегрального показателя
            weights_input = request.form.get('weights') # строка типа 
            "w1,w2,w3"
            if weights_input:
                w = [float(x) for x in weights_input.split(',')]
            else:
                w = [1.0, 1.0, 1.0]
            # Промежуточные оценки по критериям (0-100 баллов каждый)
            max_tasks = data['tasks'].max()
            max_speed = data['speed'].max()
            max_correct = data['correctness'].max() if data['correctness'].max() <= 100 else 100.0
            # Если "speed" = время выполнения задачи (меньше лучше), то можно использовать инверсию:
            # min_speed = data['speed'].min(); data['speed_score'] = min_speed / data['speed'] * 100
            data['tasks_score'] = data['tasks'] / max_tasks * 100 if max_tasks > 0 else 0
            data['speed_score'] = data['speed'] / max_speed * 100 if max_speed > 0 else 0
            data['correctness_score'] = data['correctness'] if max_correct == 100.0 else data['correctness'] / max_correct * 100
            # Итоговый рейтинг как взвешенная сумма (нормируем на сумму весов)
            total_weight = sum(w) if sum(w) != 0 else 1.0
            data['score'] = (data['tasks_score'] * w[0] +
            data['speed_score'] * w[1] +
            data['correctness_score'] * w[2]) / total_weight
            # Сохраняем текущие данные в глобальный список
            global current_employees
            current_employees = []
            for _, row in data.iterrows():
                emp = Employee(name=row['name'], tasks=row['tasks'], speed=row['speed'], correctness=row['correctness'], score=row['score'])
            current_employees.append(emp)
            # (Опционально: обновить данные в базе, если используется модель Employee)
            Employee.query.delete()
            for emp in current_employees:
                db.session.add(emp)
            db.session.commit()
            flash("Расчет эффективности выполнен успешно.", 'success')
            return redirect(url_for('views.dashboard'))
    else:
        flash("Недопустимый формат файла. Загрузите CSV.", 'error')
    # GET-запрос - форма загрузки (для администратора)
    return render_template('upload.html')