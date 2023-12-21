from django.core.exceptions import ValidationError

def validate_image_extension(value):
    import os
    ext = os.path.splitext(value.name)[1]  # Erhalte die Dateiendung
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')