from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, DateField, TimeField
from wtforms.validators import DataRequired


class EventsForm(FlaskForm):
    title = StringField('Название события', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    # date_and_time = DateTimeField("Дата и время проведения мероприятия", validators=[])
    date = DateField("Дата проведения мероприятия", format="'%d-%m-%Y'")
    time = TimeField("Время проведения мероприятия", format="%H:%M")
    place = StringField('Адрес проведения мероприятия')
    submit = SubmitField('Выложить')
