from django import forms
from django.core.validators import RegexValidator

# Валидатор, разрешающий только буквы и пробелы
alpha_space_validator = RegexValidator(
    regex=r'^[a-zA-Z\s]+$',
    message='Это что такое? Давай-ка попробуем ввести название города буковками.'
)

class CityForm(forms.Form):
    city = forms.CharField(
        max_length=100,
        validators=[alpha_space_validator],
        help_text='Ведите название города на английском языке.',
        widget=forms.TextInput(
            attrs={'placeholder': 'В городе...'})
    )