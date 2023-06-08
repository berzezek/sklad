from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, ProductInWarehouse, Credit


@receiver(post_save, sender=Order)
def create_credit_and_product_in_warehouse(sender, instance, created, **kwargs):
    if instance.status == 'paid' and created:
        # Создание экземпляра Credit
        name = f'Продажа {instance.pk}'
        description = f'Продажа от {instance.date}'
        amount = instance.get_total_order_retail_price()
        Credit.objects.create(name=name, description=description, amount=amount)

    if instance.status == 'shipped' and created and instance.warehouse:
        # Создание экземпляров ProductInWarehouse
        for product_in_order in instance.productinorder_set.all():
            ProductInWarehouse.objects.create(
                product=product_in_order.product,
                warehouse=instance.warehouse,
                quantity=product_in_order.quantity,
                transaction='out'
            )
