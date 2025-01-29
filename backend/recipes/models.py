import uuid

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (
    MAX_LENGTH_INGRIDIENT_NAME,
    MAX_LENGTH_MEASURMENT_UNIT,
    MAX_LENGTH_RECIPE_NAME,
    MAX_LENGTH_TAG_NAME,
    MAX_LENGTH_TAG_SLUG,
    MIN_AMOUNT_OF_INGREDIENT,
    MIN_COOKING_TIME_MINUTES,
)
from users.models import User


class Tag(models.Model):
    """Класс тега для классификации и поиска рецептов."""
    name = models.CharField(
        max_length=MAX_LENGTH_TAG_NAME,
        verbose_name='Тег рецепта',
        unique=True,
    )
    slug = models.SlugField(
        max_length=MAX_LENGTH_TAG_SLUG,
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def clean(self):
        if Tag.objects.filter(name__iexact=self.name).exists():
            raise ValidationError(
                f'Тег, по смыслу подобный "{self.name}" уже существует.')

        if Tag.objects.filter(slug__iexact=self.slug).exists():
            raise ValidationError(
                f'Подобный слаг "{self.slug}" уже существует.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Тег {self.name} - слаг {self.slug}.'


class Ingredient(models.Model):
    """Класс перечня всех возможных ингридиентов."""
    name = models.CharField(
        max_length=MAX_LENGTH_INGRIDIENT_NAME,
        verbose_name='Ингредиент',
        help_text='Ингредиент: обязательное поле',
    )

    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_MEASURMENT_UNIT,
        verbose_name='Единица измерения',
        help_text='Единица измерения: обязательное поле',
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='ingredient_measurement_unit_pair_unique'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}.'


class Recipe(models.Model):
    """Класс, описывающий структуру рецепта."""

    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список id тегов',
        help_text='Теги: обязательное поле',
    )
    image = models.ImageField(
        verbose_name='Фото готового блюда',
        help_text='Картинка: обязательное поле',
        upload_to='recipes/images/',
    )
    name = models.CharField(
        max_length=MAX_LENGTH_RECIPE_NAME,
        verbose_name='Название рецепта',
        help_text='Название рецепта: обязательное поле',
    )
    text = models.TextField(
        verbose_name='Описание рецепта',
        help_text='Описание рецепта: обязательное поле',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления (в минутах)',
        help_text='Время приготовления: обязательное поле',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME_MINUTES,
                message=f'Минимальное время - {MIN_COOKING_TIME_MINUTES} мин.'
            )
        ],
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name='recipes',
    )
    short_url_code = models.CharField(
        max_length=5,
        unique=True,
        editable=False
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def save(self, *args, **kwargs):
        if not self.short_url_code:
            self.short_url_code = uuid.uuid4().hex[:5]
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Рецепт {self.name} от {self.author.username}.'


class RecipeIngredient(models.Model):
    """Класс для связи рецепта, его ингридиентов, и их количества."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='+',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(
                MIN_AMOUNT_OF_INGREDIENT,
                message=(
                    'Минимальное количество любого ингредиента в рецепте: '
                    f' {MIN_AMOUNT_OF_INGREDIENT} ед.'
                )
            )
        ]
    )

    class Meta:
        ordering = ('id',)
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количество ингредиента в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='recipe_ingredient_pair_unique'
            ),
        )

    def __str__(self):
        return f'Ингредиент {self.ingredient.name}: кол-во {self.amount}'


class MutualFields(models.Model):
    """Абстрактный класс для общих полей в таблицах Favorite и ShoppingList."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='%(class)s',
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(class)s_user_recipe_unique'
            ),
        ]


class Favorite(MutualFields):
    """Класс понравившегося рецепта."""
    class Meta(MutualFields.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user} лайкнул(-а) {self.recipe}.'


class ShoppingList(MutualFields):
    """Класс списка покупок ингридиентов понравившегося рецепта."""
    class Meta(MutualFields.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'

    def __str__(self):
        return f'{self.user} купит продукты для {self.recipe}.'
