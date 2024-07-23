from django.core.validators import RegexValidator

# Validator that allows only letters and spaces
alpha_space_validator = RegexValidator(
    regex=r'^[a-zA-Z\s]+$',
    message="What is this? Let's try to enter the city name using English letters."
)
