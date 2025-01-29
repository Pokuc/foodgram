from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User, Follow


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email')})
    )
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Extra Fields', {'fields': ('avatar',)}),
    )
    list_display = ('id',
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'is_staff',
                    'avatar')
    list_editable = ('avatar',)
    ordering = ('id',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Класс настройки модели Follow в админке."""

    list_display = ('user', 'following')
    search_fields = ('user', 'following')
