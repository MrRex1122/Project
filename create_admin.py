from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin', role='admin')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print("Администратор admin/admin создан.")
    else:
        admin.set_password('admin')
        admin.role = 'admin'
        db.session.commit()
        print("Пароль администратора обновлён на admin.")