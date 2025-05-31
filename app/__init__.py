from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
import config

def create_app():
    app = Flask(__name__)
    app.config.from_object(config) # убраны скобки тк это переменная
    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    login_manager.login_view = 'auth.login' # куда перенаправлять неавторизованных
    login_manager.login_message = u"Пожалуйста, войдите в систему."

    # Регистрация user_loader(нету в инструкции)
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Регистрация блюпринтов
    from app import auth, views
    app.register_blueprint(auth.bp)
    app.register_blueprint(views.bp)

    # Создание таблиц в базе, если не созданы
    with app.app_context():
        from app.models import User  # <-- импорт перемещён сюда
        db.create_all()
        # <-- отсюда
        # Проверка наличия администратора, если нет – создание
        if User.query.filter_by(role='admin').first() is None:
            admin = User(username="admin", role="admin")
            admin.set_password("admin") # пароль по умолчанию "admin", рекомендуется сменить
            db.session.add(admin)
            db.session.commit()
    return app