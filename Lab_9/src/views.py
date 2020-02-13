from django.shortcuts import render
from src import utils, config
from ResultForm import ResultForm
from ResForm import ResForm
from django.shortcuts import redirect

def index(request):
    body, head = utils.get_table_data()

    head = utils.scrap_head()
    body = utils.get_db_results()
    # Отрисовка HTML-шаблона index.html с данными внутри
    # переменной контекста context
    return render(
        request,
        'main.html',
        context={'page_title':'Результаты ACM ICPC', 'header_row' : head, 'data_db' : body},
    )


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def add(request):
    c = {}
    form = ResForm(request.POST)
    if request.method == 'POST' and form.is_valid():
        res = [form.cleaned_data['year'], form.cleaned_data['location'], form.cleaned_data['place'], form.cleaned_data['squad'],
               form.cleaned_data['coach']]
        utils.create_result(res)
        return redirect('/')
    return render(
        request,
        'add_form.html',
        context={
            'title':'Новый результат чемпионата', 'form' : form, 'csrf' :request
        }
    )
