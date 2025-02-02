from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import NameSearchFilter, ExtraParamsFilter
from api.paginators import PageOrLimitPagination
from api.permissions import IsAuthorOrReadOnly, IsOwnerOrReadOnly
from api.serializers import (
    UserSerializer,
    FavoriteShoppingListSerializer,
    FollowSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeReadSerializer,
    TagSerializer
)
from api.utils import structure_file
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingList,
    Tag
)
from users.models import User


class UserViewSet(viewsets.GenericViewSet):
    """Вьюсет для управления и настройки пользователей."""

    queryset = User.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = PageOrLimitPagination
    filter_backends = (DjangoFilterBackend,
                       filters.OrderingFilter)
    ordering = ('-id',)
    serializer_class = UserSerializer

    @action(detail=False,
            methods=['put', 'delete'],
            url_path='me/avatar',
            permission_classes=[IsAuthenticated])
    def update_avatar(self, request):
        """Обновляет или удаляет аватар текущего пользователя."""

        if request.method == 'PUT':
            if not request.data:
                return Response({'detail': 'Файл аватарки не был передан.'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = UserSerializer(request.user,
                                        data=request.data,
                                        partial=True,
                                        context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response({"avatar": serializer.data.get('avatar')},
                                status=status.HTTP_200_OK)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            if not request.user.avatar:
                return Response({'detail': 'Аватарка отсутствует.'},
                                status=status.HTTP_400_BAD_REQUEST)
            request.user.avatar.delete()
            request.user.save()
        return Response({'detail': 'Аватарка удалена.'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=['get'],
            serializer_class=FollowSerializer,
            permission_classes=[IsAuthenticated],)
    def subscriptions(self, request, *args, **kwargs):
        """Список всех подписок пользователя."""
        user = request.user
        following = User.objects.filter(following__user=user)
        pages = self.paginate_queryset(following)
        if pages is not None:
            serializer = FollowSerializer(
                pages, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],)
    def subscribe(self, request, pk, *args, **kwargs):
        """Метод для подписки или отписки от блоггеров."""
        reader = request.user
        blogger = get_object_or_404(User, pk=pk)
        if request.method == 'POST':
            serializer = FollowSerializer(data={
                'user': reader.id, 'following': blogger.id
            }, context={'request': request})
            serializer.is_valid(raise_exception=True)

            if serializer.create_follow():
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)

        elif request.method == 'DELETE':
            if serializer.delete_follow():
                return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'message':
                             f'Вы не подписаны на {blogger.username}.'},
                            status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(ReadOnlyModelViewSet):
    """Вьюсет для получения информации о тегах списком или по id."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    """Вьюсет для получения информации о ингредиентах списком или по id."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (NameSearchFilter,)
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    """Вьюсет для пользовательский CRUD-операций с рецептами."""

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filterset_class = ExtraParamsFilter
    filter_backends = (DjangoFilterBackend,
                       filters.OrderingFilter)
    pagination_class = PageOrLimitPagination
    ordering = ('-id',)

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    @action(detail=True, methods=['get'], url_path='get-link',)
    def get_link(self, request, *args, **kwargs):
        """Получить короткую ссылку на рецепт."""
        recipe = self.get_object()
        short_link = request.build_absolute_uri(
            f'/s/{recipe.short_url_code}')
        return Response({"short-link": short_link}, status=status.HTTP_200_OK)

    def recipe_add_unadd(self, request, model, method_serializer, pk):
        """
        Общая реализация добавления/удаления рецептов
        в Favorite и в Shopping_List.
        """
        actor = request.user
        addable_recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            if model.objects.filter(user=actor,
                                    recipe=addable_recipe).exists():
                return Response('Данный рецепт уже был добавлен.',
                                status=status.HTTP_400_BAD_REQUEST)
            model.objects.create(user=actor, recipe=addable_recipe)
            serializer = method_serializer(addable_recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        try:
            unaddable_recipe = model.objects.get(user=actor,
                                                 recipe=addable_recipe)
            unaddable_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except model.DoesNotExist:
            return Response('Нечего удалять, пусто.',
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],)
    def shopping_cart(self, request, pk):
        """Добавление и удаление рецепта в ShoppingList."""
        return self.recipe_add_unadd(request,
                                     ShoppingList,
                                     FavoriteShoppingListSerializer,
                                     pk)

    @action(detail=False,
            methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request, *args, **kwargs):
        """
        Генерация списка покупок из всех рецептов, добавленных в список.
        Повторяющиеся ингридиенты складываются по их количеству.
        """
        shopping_list = (RecipeIngredient.objects
                         .filter(recipe__shoppinglist__user=request.user.id)
                         .values('ingredient__name',
                                 'ingredient__measurement_unit')
                         .annotate(amount=Sum('amount')))
        if not shopping_list.exists():
            return Response({'detail': 'Ваш список покупок пуст.'},
                            status=status.HTTP_400_BAD_REQUEST)
        download_list = structure_file(shopping_list)
        response = HttpResponse(download_list,
                                content_type='text/plain; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="qweqwe.txt"'
        return response

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=[IsAuthenticated],)
    def favorite(self, request, pk):
        """Добавление и удаление рецепта в Favorite."""
        return self.recipe_add_unadd(request,
                                     Favorite,
                                     FavoriteShoppingListSerializer,
                                     pk)


def redirect_to_full(request, short_url_code):
    """Перенаправление с короткой ссылки на исходный рецепт."""
    recipe = get_object_or_404(Recipe, short_url_code=short_url_code)
    return redirect(f'/recipes/{recipe.id}')
