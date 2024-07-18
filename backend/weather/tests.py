from django.test import TestCase
from .forms import CityForm


class CityFormTest(TestCase):
    """
    Тесты для формы ввода города.
    """

    def test_city_form_valid(self):
        """
        Проверка валидации формы с верными данными города.
        """

        form_data = {'city': 'Moscow'}
        form = CityForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_city_form_invalid(self):
        """
        Проверка валидации формы с неверными данными города.
        """

        form_data = {'city': ''}
        form = CityForm(data=form_data)
        self.assertFalse(form.is_valid())