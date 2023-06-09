from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, ProductInWarehouse, Credit, Lot, Debit


@receiver(post_save, sender=Order)
def create_credit_and_out_product_in_warehouse(sender, instance, created, **kwargs):
    if instance.status == 'paid':
        # Create an instance of Credit
        name = f'Продажа {instance.pk}'
        description = f'Продажа от {instance.date}'
        amount = instance.get_total_order_retail_price()
        consumer = instance.consumer
        consumer.total_cost += amount
        consumer.save()
        Credit.objects.create(name=name, description=description, amount=amount)

    if instance.status == 'shipped' and instance.warehouse:
        # Create instances of ProductInWarehouse
        for product_in_order in instance.productinorder_set.all():
            ProductInWarehouse.objects.create(
                product=product_in_order.product,
                warehouse=instance.warehouse,
                quantity=product_in_order.quantity,
                transaction='out'
            )


@receiver(post_save, sender=Lot)
def create_debit_for_buy_lot(sender, instance, created, **kwargs):
    if instance.status == 'paid':
        # Create an instance of Debit
        name = f'Покупка лота {instance.pk}'
        description = f'Покупка от {instance.date}'
        amount = instance.get_total_lot_purchase_price()
        Debit.objects.create(name=name, description=description, amount=amount)
