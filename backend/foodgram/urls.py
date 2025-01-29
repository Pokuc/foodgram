from django.contrib import admin
from django.urls import include, path

from api.views import redirect_to_full


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('s/<str:short_url_code>/',
         redirect_to_full,
         name='redirect_to_full'),
]
