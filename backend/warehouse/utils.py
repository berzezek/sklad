import random

from warehouse.models import *
from warehouse.services.warehouse import product_cost_price


def create_fake_products():
    for i in range(2):
        cat = Category.objects.create(name=f'Category {i + 1}')
        for j in range(2):
            Product.objects.create(
                name=f'Product {j + 1} - {cat.name}',
                category=cat,
                retail_price=random.randint(10, 100),
                description=f'Description {j}',
                weight=random.randint(10, 100)
            )


def create_fake_lots():
    products = Product.objects.all()
    for i in range(2):
        lot = Lot.objects.create(
            description=f'Description {i + 1}',
        )
        for j in products:
            ProductInLot.objects.create(
                product=j,
                lot=lot,
                quantity=random.randint(10, 50),
                purchase_price=random.randint(10, 100)
            )
        for _ in range(2):
            LotCost.objects.create(
                name='transportation',
                lot=lot,
                distribution='equal',
                amount_spent=random.randint(10, 100)
            )

        for _ in range(2):
            LotCost.objects.create(
                name='customs',
                lot=lot,
                distribution='by_weight',
                amount_spent=random.randint(10, 100)
            )

        for _ in range(2):
            LotCost.objects.create(
                name='other',
                lot=lot,
                distribution='by_price',
                amount_spent=random.randint(10, 100)
            )


def create_fake_warehouse():
    Warehouse.objects.create(name='Main warehouse')


def transfer_from_lot_to_warehouse():
    lots = Lot.objects.all()
    warehouse = Warehouse.objects.first()
    for lot in lots:
        lot.status = 'delivered'
        lot.save()
        for product_in_lot in lot.productinlot_set.all():
            ProductInWarehouse.objects.create(
                product=product_in_lot.product,
                warehouse=warehouse,
                quantity=product_in_lot.quantity,
                cost_price=product_cost_price(lot.pk, product_in_lot.product.pk),
                transaction='in',
            )
        lot.status = 'in_warehouse'
        lot.save()


def create_fake_sales():
    products = Product.objects.all()
    for i in range(2):
        con = Consumer.objects.create(
            name=f'Consumer {i + 1}',
        )
        for j in range(3):
            order = Order.objects.create(
                warehouse=Warehouse.objects.first(),
                consumer=con,
            )
            for k in products:
                ProductInOrder.objects.create(
                    product=k,
                    order=order,
                    quantity=random.randint(1, 10),
                )


def main():
    create_fake_products()
    create_fake_lots()
    create_fake_warehouse()
    transfer_from_lot_to_warehouse()
    create_fake_sales()
