def structure_file(user_shopping_list):
    """Создание структуры файла списка покупок."""
    structured_list = []
    structured_list.append('Ингридеинты для всех рецептов:\n')
    for ingredient in user_shopping_list:
        structured_list.append(
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measurement_unit"]}) — '
            f'{ingredient["amount"]}')
    structured_list.append('==============================\n')
    return '\n'.join(structured_list)
