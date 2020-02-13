from django.forms import ModelForm
from src.models import Result

class ResForm(ModelForm):
     class Meta:
        model = Result
        fields = ['year', 'location', 'place', 'squad', 'coach',  ]