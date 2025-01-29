from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers

from api.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet,
)

app_name = 'api'

router = routers.DefaultRouter()

router.register('users', UserViewSet, basename='users')
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
