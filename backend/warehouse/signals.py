from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Q

from .models import Order, ProductInWarehouse, Lot, Cost
from django.dispatch import Signal

# Define the signal
lot_costs_excluded = Signal(providing_args=['instance', 'excluded_lot_costs'])


@receiver(post_save, sender=Order)
def create_cost_in_and_out_product_in_warehouse(sender, instance, created, **kwargs):
    if instance.status == 'paid':
        # Create an instance of Credit
        name = f'Продажа {instance.pk}'
        description = f'Продажа от {instance.date}'
        amount = instance.get_total_order_retail_price()
        consumer = instance.consumer
        consumer.total_cost += amount
        consumer.save()
        Cost.objects.create(name=name, description=description, amount=amount, transaction='in')

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
def create_cost_out_for_buy_lot(sender, instance, created, **kwargs):
    if created and instance.status == 'paid':
        # Проверяем, существует ли уже запись для данного лота
        existing_cost_out = Cost.objects.filter(name=f'Оплата лота {instance.pk}').exists()

        if not existing_cost_out:
            # Создаем объект Cost только если его еще нет
            name = f'Оплата лота {instance.pk}'
            description = f'Оплата за товары лота #{instance.pk} от {instance.date}'
            amount = instance.get_total_lot_purchase_price()
            date = instance.date
            Cost.objects.create(name=name, description=description, amount=amount, date=date, transaction='out')

        lot_costs = instance.lotcost_set.all()

        for lot_cost in lot_costs:
            # Проверяем, существует ли уже запись для данного расхода на лот
            existing_cost_out = Cost.objects.filter(name=f'Затраты {lot_cost.pk} на лот #{instance.pk}').exists()

            if not existing_cost_out:
                # Создаем объект Cost только если его еще нет
                name = f'Затраты {lot_cost.pk} на лот #{instance.pk}'
                description = f'Затраты #{lot_cost.pk} ({lot_cost.get_display_name()}) от {lot_cost.date} ' \
                              f'на лот #{instance.pk} от {instance.date}'
                amount = lot_cost.amount_spent
                date = lot_cost.date
                Cost.objects.create(name=name, description=description, amount=amount, date=date, transaction='out')


@receiver(post_save, sender=Lot)
def check_lot_costs(sender, instance, created, **kwargs):
    if instance.status == 'paid':
        # Get existing cost_out expenses related to the lot
        existing_costs_out = Cost.objects.filter(Q(name__startswith=f'Затраты {instance.pk} на лот')
                                               | Q(name__startswith=f'Оплата лота {instance.pk}'))

        existing_cost_out_names = [cost_out.name for cost_out in existing_costs_out]

        # Get lot costs that were not included in cost_out
        excluded_lot_costs = instance.lotcost_set.exclude(name__in=existing_cost_out_names)

        # Send signal indicating excluded lot costs
        lot_costs_excluded.send(sender=Lot, instance=instance, excluded_lot_costs=excluded_lot_costs)