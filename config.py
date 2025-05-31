import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Основные настройки
SECRET_KEY = "S0me$ecretKey" # секретный ключ для сессий и защиты форм
SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "app.db") # 
#путь к базе SQLite
SQLALCHEMY_TRACK_MODIFICATIONS = False # отключение лишних предупреждений 

# Настройки загрузки файлов
UPLOAD_FOLDER = os.path.join(BASE_DIR, "data")
ALLOWED_EXTENSIONS = {"csv"}
# Параметры по умолчанию для расчета
DEFAULT_WEIGHTS = {"tasks": 1.0, "speed": 1.0, "accuracy": 1.0}