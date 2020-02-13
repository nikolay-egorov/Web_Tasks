from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class ResultForm(FlaskForm):
    year = IntegerField('Год', validators=[DataRequired()])
    location = StringField('Место проведения', validators=[DataRequired()])
    place = StringField('Место', validators=[DataRequired()])
    squad = StringField('Состав команды', validators=[DataRequired()])
    coach = StringField('Тренер')
    submit = SubmitField('Добавить запись')
