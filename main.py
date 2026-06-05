from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_required, login_user, current_user, logout_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///diary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'lol'

db = SQLAlchemy(app)
login_manager = LoginManager(app)

# Модели базы данных
class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    subtitle = db.Column(db.String(200))
    text = db.Column(db.Text, nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.query(Users).get(user_id)

@app.route('/')
def index_redirect():
    """Перенаправляет с корневого URL на страницу home"""
    return redirect(url_for('home'))

@app.route('/home')
def home():
    """Домашняя страница (до авторизации)"""
    return render_template('home.html')

@app.route('/register', methods=["GET", "POST"])
def register():
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Проверяем, существует ли пользователь
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('register.html', error='Пользователь уже существует')

        # Хэшируем пароль
        hashed_password = generate_password_hash(password)
        new_user = Users(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login/", methods=["GET", "POST"])
def login():
    """Авторизация пользователя"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Неверные логин или пароль')
    return render_template('login.html')

@app.route('/logout/')
@login_required
def logout():
    """Выход из системы"""
    logout_user()
    return redirect(url_for('home'))

@app.route('/index')
@login_required
def index():
    """Главная страница после авторизации — отображение всех карточек"""
    cards = Card.query.all()
    return render_template('index.html', cards=cards)

@app.route('/card/<int:id>')
@login_required
def card(id):
    """Просмотр отдельной карточки по ID"""
    card = Card.query.get_or_404(id)
    return render_template('card.html', card=card)

@app.route('/create')
@login_required
def create():
    """Страница создания новой карточки"""
    return render_template('create.html')

@app.route('/form_create', methods=['GET', 'POST'])
@login_required
def form_create():
    """Обработка формы создания карточки"""
    if request.method == 'POST':
        title = request.form.get('title')
        subtitle = request.form.get('subtitle')
        text = request.form.get('text')

        new_card = Card(title=title, subtitle=subtitle, text=text)
        db.session.add(new_card)
        db.session.commit()

        return redirect(url_for('index'))
    return redirect(url_for('create'))

# Инициализация базы данных — создание таблиц при запуске
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
