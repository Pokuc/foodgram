from django_filters import rest_framework as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag
from users.models import User


class NameSearchFilter(SearchFilter):
    search_param = 'name'


class ExtraParamsFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(field_name='tags__slug',
                                             to_field_name='slug',
                                             queryset=Tag.objects.all())
    is_favorited = filters.BooleanFilter(method='get_favorited_filter',
                                         label='В Избранном')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_shopping_cart_filter',
        label='В Списке покупок')

    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='author',
        label='Авторы'
    )

    def get_favorited_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)
        return queryset

    def get_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shoppinglist__user=user)
        return queryset

    class Meta:
        model = Recipe
        fields = ('author', 'tags', 'is_favorited', 'is_in_shopping_cart')
