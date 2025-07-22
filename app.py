import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import generate_password_hash
from extensions import db, login_manager  # Импорт из нового модуля

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Flask app creation
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "trampoline-park-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database config
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///trampoline_park.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Telegram config
app.config["TELEGRAM_TOKEN"] = os.environ.get("TELEGRAM_TOKEN", "")
app.config["WEBHOOK_URL"] = os.environ.get("WEBHOOK_URL", "")

# Init extensions
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к панели управления.'

@login_manager.user_loader
def load_user(user_id):
    # Отложенный импорт для избежания циклических зависимостей
    from project_models import Admin
    return Admin.query.get(int(user_id))

# Импорт маршрутов и моделей ПОСЛЕ инициализации приложения
from project_models import Admin
import routes
import bot

with app.app_context():
    # Создание таблиц
    db.create_all()

    # Создание дефолтного админа, если его нет
    if not Admin.query.first():
        admin = Admin(
            username='admin',
            email='admin@trampolinepark.ru',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
        logging.info("Default admin user created: admin/admin123")
