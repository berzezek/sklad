import random

from warehouse.models import *


def create_fake_products():
    for i in range(1, 10):
        cat = Category.objects.create(name=f'Category {i}')
        for j in range(1, 10):
            Product.objects.create(
                name=f'Product {j} - {cat.name}',
                category=cat,
                retail_price=random.randint(10, 100),
                description=f'Description {j}',
                weight=random.randint(10, 100)
            )


def create_fake_lots():
    products = Product.objects.all()
    for i in range(1, 10):
        Lot.objects.create(
            name=f'Lot {i}',
            description=f'Description {i}',
        )
        for j in products:
            ProductInLot.objects.create(
                product=j,
                lot=Lot.objects.get(name=f'Lot {i}'),
                quantity=random.randint(10, 50),
                purchase_price=random.randint(10, 100)
            )
        for _ in range(1, 2):
            LotCost.objects.create(
                name='transportation',
                lot=Lot.objects.get(name=f'Lot {i}'),
                distribution='equal',
                amount=random.randint(10, 100)
            )

        for _ in range(1, 2):
            LotCost.objects.create(
                name='customs',
                lot=Lot.objects.get(name=f'Lot {i}'),
                distribution='by_weight',
                amount=random.randint(10, 100)
            )

        for _ in range(1, 2):
            LotCost.objects.create(
                name='other',
                lot=Lot.objects.get(name=f'Lot {i}'),
                distribution='by_price',
                amount=random.randint(10, 100)
            )


def create_fake_warehouse():
    Warehouse.objects.create(name='Main warehouse')


def main():
    create_fake_products()
    create_fake_lots()
    create_fake_warehouse()


