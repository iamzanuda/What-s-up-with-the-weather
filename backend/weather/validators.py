from django.core.validators import RegexValidator

# Валидатор, разрешающий только буквы и пробелы
alpha_space_validator = RegexValidator(
    regex=r'^[a-zA-Z\s]+$',
    message='Это что такое? Давай-ка попробуем ввести название города английскими буковками.'
)