from django.core.exceptions import ValidationError

def validate_area(value):
    if value < 0:
        raise ValidationError('Площадь должна быть больше 0.')
