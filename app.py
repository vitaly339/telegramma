import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
import os
import logging
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask import Flask, render_template
from werkzeug.security import generate_password_hash
from flask_login import logout_user
from flask import redirect, url_for
from extensions import db, login_manager # Импорт из нового модуля

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Flask app creation
app = Flask(__name__)

@app.route('/customers')
def customers():
    return render_template('customers.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/bookings')
def bookings():
    return render_template('bookings.html')

@app.route('/')
def index():
    return render_template('login.html')

    return render_template('login.html')

    from flask import request, redirect, url_for
    from flask_login import login_user
    from werkzeug.security import check_password_hash
    from project_models import Admin

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = Admin.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('admin'))  # Измени на нужный маршрут
        else:
            return render_template('login.html', error='Неверный логин или пароль')

    return render_template('login.html')
    
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

# 💡 ЭТО ВАЖНО: Запуск сервера
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
