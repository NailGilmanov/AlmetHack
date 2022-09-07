from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, DateTimeField
from wtforms.validators import DataRequired


class EventsForm(FlaskForm):
    title = StringField('Название события', validators=[DataRequired()])
    content = TextAreaField("Содержание")
    date_and_time = DateTimeField("Дата и время проведения мероприятия", format='%d-%m-%Y %H:%M')
    place = StringField('Адрес проведения мероприятия')
    is_private = BooleanField("Скрытый")
    submit = SubmitField('Выложить')
