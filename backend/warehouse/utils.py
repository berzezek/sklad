import random

from django.db.models import Q

from warehouse.models import *


def add_costs_out_from_lot_if_not_exists(lot):
    existing_costs_out = Cost.objects.filter(Q(name__startswith=f'Затраты {lot.pk} на лот')
                                           | Q(name__startswith=f'Оплата лота {lot.pk}'))

    existing_cost_out_names = [ cost_out.name for cost_out in existing_costs_out ]

    # Проверяем, существует ли уже запись для оплаты лота
    existing_payment_cost_out = Cost.objects.filter(name=f'Оплата лота {lot.pk}').exists()

    if not existing_payment_cost_out:
        # Создаем объект Cost только если его еще нет
        name = f'Оплата лота {lot.pk}'
        description = f'Оплата за товары лота #{lot.pk} от {lot.date}'
        amount = lot.get_total_lot_purchase_price()
        date = lot.date
        Cost.objects.create(name=name, description=description, amount=amount, date=date, transaction='out')

    # Создаем затраты в Cost только для тех расходов, которые ранее не были добавлены
    lot_costs = LotCost.objects.filter(lot__pk=lot.pk).exclude(name__in=existing_cost_out_names)
    for lot_cost in lot_costs:
        # Проверяем, существует ли уже запись для данного расхода на лот
        existing_cost_out = Cost.objects.filter(
            name=f'Затраты {lot_cost.pk} на лот #{lot.pk}').exists()

        if not existing_cost_out:
            # Создаем объект Cost только если его еще нет
            name = f'Затраты {lot_cost.pk} на лот #{lot.pk}'
            description = f'Затраты #{lot_cost.pk} ({lot_cost.get_display_name()}) от {lot_cost.date} ' \
                          f'на лот #{lot.pk} от {lot.date}'
            amount = lot_cost.amount_spent
            date = lot_cost.date
            Cost.objects.create(name=name, description=description, amount=amount, date=date, transaction='out')

