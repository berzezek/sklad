import csv
from urllib.parse import quote

from django.http import HttpResponse
from django.utils.timezone import now

from ..models import Product


def product_to_csv(request):
    filename = f'Справочник продуктов от {now().strftime("%Y-%m-%d")}.csv'
    response = HttpResponse(content_type='text/csv')
    response[ 'Content-Disposition' ] = f'attachment; filename*=UTF-8\'\'{quote(filename)}'

    writer = csv.writer(response)
    writer.writerow([ "#", "Наименование", "Розничная цена", "Вес кг." ])

    products = Product.objects.all()
    for product in products:
        writer.writerow([ product.id, product.name, product.retail_price, product.weight ])
    writer.writerow([ ])  # Пустая строка
    writer.writerow([ '', 'Ответственный', '______', 'Иванов А.Н' ])
    writer.writerow([ '', 'Принял', '______', 'Петров К.Е.' ])
    return response
