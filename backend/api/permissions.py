from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Запрещает пользователям изменять чужие данные профилей.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated if view.action == 'me' else True

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj == request.user)


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Доступ к редактированию рецепта для автора.
    Для остальных категорий пользователей доступ только на чтение.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == obj.author)
