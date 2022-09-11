from flask import Flask, render_template_string
from data import db_session
from waitress import serve


from forms.user import RegisterForm, LoginForm
from forms.events import EventsForm
from forms.comments import CommentsForm

from data.users import User
from data.events import Events
from data.comments import Comment

from flask_login import LoginManager, login_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register/<string:username>/<string:password>/<string:password_again>/<string:description>', methods=['GET', 'POST'])
def valid_register_data(username, password, password_again, description):
    form = RegisterForm()
    if form.validate_on_submit():
        if password != password_again:
            # Пароли не совпадают
            return render_template_string("false")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.name == username).first():
            # Такой пользователь уже есть
            return render_template_string("false")

    # Добавление в базу данных
    db_sess = db_session.create_session()
    user = User(
        name=username,
        about=description
    )
    user.set_password(password)
    db_sess.add(user)
    db_sess.commit()

    return render_template_string("true")


@app.route('/login/<string:username>/<string:password>')
def valid_login_data(username, password):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.name == username).first()

    if user:
        if user.check_password(password):
            login_user(user)
            return render_template_string('true')
        # Неправильный логин или пароль
    return render_template_string('false')


@app.route("/new_event/<string:title>/<string:content>/<string:date>/<string:time>/<string:place>/<int:category>",
           methods=['GET', 'POST'])
def new_event(title, content, date, time, place, category):
    session = db_session.create_session()

    event = Events()
    event.title = title
    event.content = content
    event.place = place
    event.date = date
    event.time = time
    event.category = category
    current_user.events.append(event)
    session.merge(current_user)
    session.commit()
    return render_template_string('true')
    # print(form.errors)


@app.route('/get_user/<int:id>')
def get_user(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    id = f'"id":"{str(user.id)}",'
    name = f'"name":"{user.name}",'
    about = f'"about":"{user.about}",'
    rate = f'"rate":"{str(user.rate)}"'
    return render_template_string("{" + id + name + about + rate + "}")


def get_username(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == id).first()
    return user.name


@app.route('/get_user_events/<int:id>')
def get_user_events(id):
    db_sess = db_session.create_session()
    events = db_sess.query(Events).filter(Events.user_id == id).all()
    events_ids = [event.id for event in events]
    return render_template_string(str(events_ids))


@app.route('/get_event/<int:id>')
def get_event(id):
    db_sess = db_session.create_session()
    event = db_sess.query(Events).filter(Events.id == id).first()
    id = f'"id":"{str(event.id)}",'
    title = f'"title":"{event.title}",'
    content = f'"content":"{event.content}",'
    date = f'"date":"{event.date}",'
    time = f'"time":"{event.time}",'
    place = f'"place":"{event.place}",'
    category = f'"category":"{event.category}",'
    is_private = f'"is_private":"{event.is_private}",'
    user_id = f'"user_id":"{event.user_id}"'
    return render_template_string("{" + id + title + content + date + time + place + category + is_private + user_id + "}")


@app.route("/new_comment/<int:event_id>/<int:user_id>/<string:content>",
           methods=['GET', 'POST'])
def new_comment(event_id, user_id, content):
    db_sess = db_session.create_session()

    comment = Comment()
    comment.event_id = event_id
    comment.user_id = user_id
    comment.content = content

    db_sess.add(comment)
    db_sess.commit()
    return render_template_string('true')


@app.route('/get_comments/<int:id>')
def get_comments(id):
    db_sess = db_session.create_session()
    comments = db_sess.query(Comment).filter(Comment.event_id == id).all()
    response = [[get_username(comment.user_id), comment.content] for comment in comments]
    return render_template_string(str(response))


@app.route('/add_rate/<int:user_id>/<int:rate>')
def add_rate(user_id, rate):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == user_id).first()
    user.rate += rate
    db_sess.commit()
    return render_template_string('true')


def main():
    db_session.global_init('db/database.sqlite')
    print("server just started on http://127.0.0.1:4000")
    serve(app, host='0.0.0.0', port=4000)


if __name__ == '__main__':
    main()
