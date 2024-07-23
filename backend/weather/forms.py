from django import forms

from .validators import alpha_space_validator


class CityForm(forms.Form):
    """
    Form for entering the name of a city.

    Attributes:
    city (forms.CharField): Input field for the city name.
    Maximum length is 100 characters.
        - validators: List of validators for input validation.
            Uses alpha_space_validator to ensure the input
            consists only of letters and spaces.
        - help_text: Hint for the user to enter the city name
            in English.
        - widget: Widget for displaying the input field.
            Uses TextInput with the placeholder attribute
            to display the text "In the city..." before data entry.
    """

    city = forms.CharField(
        max_length=100,
        validators=[alpha_space_validator],
        help_text='Enter the city name in English.',
        widget=forms.TextInput(
            attrs={'placeholder': 'In the city...'})
    )
