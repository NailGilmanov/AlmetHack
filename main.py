from flask import Flask, render_template, redirect
from data import db_session
from waitress import serve

from forms.user import RegisterForm, LoginForm
from forms.events import EventsForm

from data.users import User
from data.events import Events

from flask_login import LoginManager, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/new_event", methods=['GET', 'POST'])
def new_event():
    form = EventsForm()
    session = db_session.create_session()
    if form.validate_on_submit():
        event = Events()
        event.title = form.title.data
        event.content = form.content.data
        event.is_private = form.is_private.data
        event.place = form.place.data
        event.date_and_time = form.date_and_time.data
        current_user.events.append(event)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template("new_event.html", title='Новое событие',
                           form=form)


@app.route('/success')
def success():
    return redirect("/")


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/')
def index():
    return render_template('index.html')


def main():
    db_session.global_init('db/database.sqlite')
    print("server just started on http://127.0.0.1:4000")
    serve(app, host='127.0.0.1', port=4000)


if __name__ == '__main__':
    main()
