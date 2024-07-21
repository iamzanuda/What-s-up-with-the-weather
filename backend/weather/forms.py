from django import forms

from .validators import alpha_space_validator

class CityForm(forms.Form):
    """
    Форма для ввода названия города.

    Атрибуты:
    city (forms.CharField): Поле ввода для названия города. 
    Максимальная длина - 100 символов.
        - validators: Список валидаторов для проверки ввода. 
            Используется alpha_space_validator для проверки, 
            что ввод состоит только из букв и пробелов.
        - help_text: Подсказка для пользователя, 
            чтобы ввести название города на английском языке.
        - widget: Виджет для отображения поля ввода. 
            Используется TextInput с атрибутом placeholder для 
            отображения текста "В городе..." до ввода данных.
    """

    city = forms.CharField(
        max_length=100,
        validators=[alpha_space_validator],
        help_text='Ведите название города на английском языке.',
        widget=forms.TextInput(
            attrs={'placeholder': 'В городе...'})
    )