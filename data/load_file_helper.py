# утилита для подготовки файла ingredients.json
# к выгрузке в модель Ingredients.
import json

input_file = 'ingredients.json'
output_file = 'helper/ingredients_transformed.json'


def convert_to_django_fixture(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    fixture = []
    for idx, item in enumerate(data, start=1):
        fixture_item = {
            # Модель, куда будем делать выгрузку фикстуры.
            "model": "recipes.ingredient",
            "pk": idx,  # Первичный ключ
            "fields": {
                "name": item.get("name"),
                "measurement_unit": item.get("measurement_unit")
            }
        }
        fixture.append(fixture_item)

    # Запись результата в новый JSON файл
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixture, f, ensure_ascii=False, indent=4)


# Запуск функции
convert_to_django_fixture(input_file, output_file)
