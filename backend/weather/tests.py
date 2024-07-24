from django.test import TestCase
from weather.forms import CityForm


class CityFormTest(TestCase):
    """
    Tests for the city input form.
    """

    def test_city_form_valid(self):
        """
        Check form validation with correct city data.
        """

        form_data = {'city': 'Moscow'}
        form = CityForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_city_form_invalid(self):
        """
        Check form validation with incorrect city data.
        """

        form_data = {'city': 'Moscow123'}
        form = CityForm(data=form_data)
        self.assertFalse(form.is_valid())
