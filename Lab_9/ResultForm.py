from wtforms_django.orm import model_form
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
from src.models import Result

ResultFormBase = model_form(Result)



class ResultForm(ResultFormBase):
    year = IntegerField('Год', validators=[DataRequired()])
    location = StringField('Место проведения', validators=[DataRequired()])
    place = StringField('Место', validators=[DataRequired()])
    squad = StringField('Состав команды', validators=[DataRequired()])
    coach = StringField('Тренер')
    submit = SubmitField('Добавить запись')
