from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils import timezone


class Result(models.Model):
    year = models.IntegerField('Год'  )
    location = models.TextField('Место проведения', max_length=30)
    place = models.TextField('Место', max_length=30)
    squad = models.TextField('Состав команды', max_length=60)
    coach = models.TextField('Тренер', max_length=50)


    # year = IntegerField('Год', validators=[DataRequired()])
    # location = StringField('Место проведения', validators=[DataRequired()])
    # place = StringField('Место', validators=[DataRequired()])
    # squad = StringField('Состав команды', validators=[DataRequired()])
    # coach = StringField('Тренер')
    # submit = SubmitField('Добавить запись')
