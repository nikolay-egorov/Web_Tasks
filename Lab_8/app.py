from flask import Flask
from flask import render_template, flash, redirect
from src import utils, config
from ResultForm import ResultForm

app = Flask(__name__)
import os

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/')
def index():

    body, head = utils.get_table_data()

    head = utils.scrap_head()
    body = utils.get_db_results()

    return render_template("main.html", page_title='Результаты ACM ICPC', header_row=head ,data_db = body )


@app.route('/add', methods=['GET', 'POST'] )
def login():
    form = ResultForm()
    if form.validate_on_submit():
        flash('Результат сохранен')
        res = [form.year.data, form.location.data, form.place.data, form.squad.data, form.coach.data ]
        utils.create_result(res)
        return redirect('/')
    return render_template('add_form.html', title='Новый результат чемпионата', form=form)


if __name__ == '__main__':

    app.run()
