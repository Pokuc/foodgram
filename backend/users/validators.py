from django.core.exceptions import ValidationError

from users.constants import (
    MAX_FILE_SIZE_AVATAR,
)


def validate_image_size(image):
    file_size = image.file.size
    if file_size > MAX_FILE_SIZE_AVATAR * 1024 * 1024:
        raise ValidationError(
            f'Размер файла не должен превышать {MAX_FILE_SIZE_AVATAR} МБ.'
        )


def validate_image_format(image):
    valid_formats = ['.png', '.jpg', '.jpeg']
    if not any(image.name.endswith(fmt) for fmt in valid_formats):
        raise ValidationError('Разрешены только файлы формата PNG, JPG, JPEG.')
