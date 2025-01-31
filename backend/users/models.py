from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from users.constants import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_FIRST_NAME,
    MAX_LENGTH_LAST_NAME,
    MAX_LENGTH_USERNAME,
)
from users.validators import (
    validate_image_format,
    validate_image_size,
)


class User(AbstractUser):
    """Расширенный класс Пользователя в Foodgram."""

    email = models.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        verbose_name='Электронная почта',
        help_text='Адрес электронной почты: обязательное поле',
        unique=True,
    )
    username = models.CharField(
        max_length=MAX_LENGTH_USERNAME,
        verbose_name='Юзернейм',
        help_text='Имя пользователя: обязательное поле',
        unique=True,
        validators=[UnicodeUsernameValidator()],
    )
    first_name = models.CharField(
        max_length=MAX_LENGTH_FIRST_NAME,
        verbose_name='Имя',
        help_text='Имя: обязательное поле',
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        max_length=MAX_LENGTH_LAST_NAME,
        verbose_name='Фамилия',
        help_text='Фамилия: обязательное поле',
        blank=False,
        null=False,
    )
    avatar = models.ImageField(
        verbose_name='Картинка пользователя',
        help_text='Вы можете загрузить аватарку',
        upload_to='users/',
        validators=[validate_image_size, validate_image_format],
        blank=True,
        null=True
    )

    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Класс модели Подписок юзеров на блогеров."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',)
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Кулинарный блогер',)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_reader_to_blogger_constraint'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='prevent_self_follow'
            ), ]

    def __str__(self):
        return (
            f'Юзер {self.user.username} читает блогера '
            f'{self.following.username}'
        )
