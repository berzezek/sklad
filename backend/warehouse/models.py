from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from simple_history.models import HistoricalRecords

"""
Модели справочников
"""


class Category(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=100, unique=True)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=100, unique=True)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    weight = models.DecimalField(verbose_name='Вес в кг', max_digits=10, decimal_places=2, default=0)
    retail_price = models.DecimalField(verbose_name='Розничная цена', max_digits=10, decimal_places=2)
    history = HistoricalRecords()


    def is_available_in_warehouse(self):
        return ProductInWarehouse.objects.filter(product=self).exists()

    def __str__(self):
        return f'{self.name} ({round(self.weight)} кг.) - {round(self.retail_price)}'


"""
Модели для лотов
"""


class ProductInLot(models.Model):
    product = models.ForeignKey(Product, verbose_name='Товар', on_delete=models.CASCADE)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    quantity = models.DecimalField(verbose_name='Количество', max_digits=10, decimal_places=2)
    purchase_price = models.DecimalField(verbose_name='Закупочная цена', max_digits=10, decimal_places=2)
    lot = models.ForeignKey('Lot', verbose_name='Заказ', on_delete=models.CASCADE)
    history = HistoricalRecords()

    def get_total_purchase_price(self):
        return self.quantity*self.purchase_price

    def get_total_weight(self):
        return self.quantity*self.product.weight

    def __str__(self):
        return f"{self.product.product.name} - {self.quantity} - {round(self.purchase_price)}"


class LotCost(models.Model):
    LOT_COST_CHOICES = [
        ('transportation', 'транспортировка'),
        ('customs', 'таможня'),
        ('other', 'другое'),
    ]
    DISTRIBUTION_CHOICES = [
        ('equal', 'поровну'),
        ('by_weight', 'по весу'),
        ('by_price', 'по цене'),
    ]
    name = models.CharField(verbose_name='Наименование', max_length=32, choices=LOT_COST_CHOICES)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    date = models.DateField(verbose_name='Дата создания', auto_now_add=True)
    update_date = models.DateField(verbose_name='Дата изменения', auto_now=True)
    distribution = models.CharField(verbose_name='Способ распределения', max_length=10, choices=DISTRIBUTION_CHOICES)
    amount_spent = models.DecimalField(verbose_name='Потраченная сумма', max_digits=10, decimal_places=2)
    lot = models.ForeignKey('Lot', verbose_name='Закупка', on_delete=models.CASCADE)
    history = HistoricalRecords()

    def get_distribution_display(self):
        distribution_display = dict(self.DISTRIBUTION_CHOICES)
        return distribution_display.get(self.distribution, self.distribution)

    def get_display_name(self):
        name_display = dict(self.LOT_COST_CHOICES)
        return name_display.get(self.name, self.name)

    def __str__(self):
        return f"{self.date} - {round(self.amount_spent)}"


class Lot(models.Model):
    STATUS_CHOICES = [
        ('new', 'новый'),
        ('paid', 'оплачен'),
        ('delivered', 'доставлен'),
        ('delivered_to_warehouse', 'доставлен на склад'),
    ]

    date = models.DateField(verbose_name='Дата создания', auto_now_add=True)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    update_date = models.DateField(verbose_name='Дата изменения', auto_now=True)
    status = models.CharField(verbose_name='Статус', max_length=32, choices=STATUS_CHOICES, default='new')
    history = HistoricalRecords()

    def get_total_lot_purchase_price(self):
        return sum([ p.get_total_purchase_price() for p in self.productinlot_set.all() ])

    def get_products_quantity(self):
        return sum([ p.quantity for p in self.productinlot_set.all() ])

    def get_products_weight(self):
        return sum([ p.get_total_weight() for p in self.productinlot_set.all() ])

    def get_total_lot_amount_spent(self):
        return sum([ c.amount_spent for c in self.lotcost_set.all() ])

    def get_total(self):
        return self.get_total_lot_purchase_price() + self.get_total_lot_amount_spent()

    def get_status_display(self):
        status_display = dict(self.STATUS_CHOICES)
        return status_display.get(self.status, self.status)

    def clean(self):
        if self.status == 'delivered_to_warehouse':
            raise ValidationError('Так принимать заказы на склад нельзя! перейдите на склад и примите заказ там!')

    def __str__(self):
        return f"{self.date} - {self.get_status_display()}"


"""
Модели для склада
"""


class Warehouse(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=100, unique=True)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)

    def get_total_warehouse_cost_price(self):
        return sum([ p.get_total_cost_price() for p in self.productinwarehouse_set.all() ])

    def get_total_warehouse_retail_price(self):
        return sum([ p.get_total_retail_price() for p in self.productinwarehouse_set.all() ])

    def get_product_count(self):
        return self.productinwarehouse_set.values('product').distinct().count()

    def __str__(self):
        return f"{self.name}"


class ProductInWarehouse(models.Model):
    TRANSACTION_CHOICES = [
        ('in', 'приход'),
        ('out', 'расход'),
        ('return', 'возврат'),
        ('write_off', 'списание'),
    ]
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE)
    date = models.DateField(verbose_name='Дата', auto_now_add=True)
    warehouse = models.ForeignKey(Warehouse, verbose_name='Склад', on_delete=models.CASCADE)
    quantity = models.DecimalField(verbose_name='Количество', max_digits=10, decimal_places=2, null=True)
    cost_price = models.DecimalField(verbose_name='Себестоимость', max_digits=10, decimal_places=2, null=True)
    transaction = models.CharField(verbose_name='Транзакция', max_length=10, choices=TRANSACTION_CHOICES)

    def get_total_cost_price(self):
        if self.transaction in [ 'in', 'return' ]:
            return self.quantity*self.cost_price
        else:
            return -self.quantity*self.cost_price

    def get_total_retail_price(self):
        if self.transaction in [ 'in', 'return' ]:
            return self.quantity*self.product.retail_price
        else:
            return -self.quantity*self.product.retail_price

    def get_total_weight(self):
        if self.transaction in [ 'in', 'return' ]:
            return self.quantity*self.product.weight
        else:
            return -self.quantity*self.product.weight

    def get_total_quantity(self):
        if self.transaction in [ 'in', 'return' ]:
            return self.quantity
        else:
            return -self.quantity

    def get_transaction_display(self):
        transaction_display = dict(self.TRANSACTION_CHOICES)
        return transaction_display.get(self.transaction, self.transaction)

    def clean(self):
        if self.get_total_quantity() < 0:
            raise ValidationError('Количество не может быть отрицательным!')

    def __str__(self):
        return f"{self.product} - {self.quantity}"


"""
Модели для продажи
"""


class Consumer(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=100, unique=True)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    total_cost = models.DecimalField(verbose_name='Сумма покупок', max_digits=12, decimal_places=2, default=0)
    level = models.IntegerField(verbose_name='Уровень', default=1)

    def __str__(self):
        return f"{self.name} - {round(self.total_cost)}"


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'новый'),
        ('paid', 'оплачен'),
        ('shipped', 'отправлен'),
    ]
    date = models.DateField(auto_now_add=True)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    update_date = models.DateField(auto_now=True)
    consumer = models.ForeignKey(Consumer, verbose_name='Покупатель', on_delete=models.CASCADE)
    status = models.CharField(verbose_name='Статус покупки', max_length=32, choices=STATUS_CHOICES, default='new')
    warehouse = models.ForeignKey(Warehouse, verbose_name='Склад', on_delete=models.CASCADE, null=True, blank=True)
    history = HistoricalRecords()

    def get_total_order_retail_price(self):
        return sum([ p.get_total_retail_price() for p in self.productinorder_set.all() ])

    def get_total_order_weight(self):
        return sum([ p.get_total_weight() for p in self.productinorder_set.all() ])

    def get_status_display(self):
        status_display = dict(self.STATUS_CHOICES)
        return status_display.get(self.status, self.status)

    def __str__(self):
        return f"{self.date} - {self.consumer}"


class ProductInOrder(models.Model):
    product = models.ForeignKey(Product, verbose_name='Продукт', on_delete=models.CASCADE)
    order = models.ForeignKey(Order, verbose_name='Заказ', on_delete=models.CASCADE)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    quantity = models.DecimalField(verbose_name='Количество', max_digits=10, decimal_places=2)
    history = HistoricalRecords()

    def get_total_retail_price(self):
        return self.quantity*self.product.retail_price

    def get_total_cost_price(self):
        cost_price = ProductInWarehouse.objects.get(product=self.product).cost_price
        return self.quantity*cost_price

    def get_total_weight(self):
        return self.quantity*self.product.weight

    def get_product_quantity_in_warehouse(self):
        return sum([ p.get_total_quantity() for p in self.product.productinwarehouse_set.all() ])

    def clean(self):
        super().clean()
        if not self.product.is_available_in_warehouse():
            raise ValidationError(f"Продукт {self.product} недоступен на складе.")

    def __str__(self):
        return f"{self.product} - {self.quantity} - {round(self.product.retail_price)}"


"""
Модели баланса
"""

class Cost(models.Model):
    name = models.CharField(verbose_name='Наименование', max_length=32)
    description = models.TextField(verbose_name='Описание', null=True, blank=True)
    amount = models.DecimalField(verbose_name='Сумма', max_digits=12, decimal_places=2)
    transaction = models.CharField(verbose_name='Вид прихода', max_length=10, choices=[('in', 'приход'), ('out', 'расход')])
    date = models.DateField(verbose_name='Дата создания', default=timezone.now)
    history = HistoricalRecords()

    def __str__(self):
        return f"Расход {self.name} - {round(self.amount)}"
    