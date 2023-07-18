from datetime import date
from django.utils import timezone

from django import forms
from django.utils.timezone import now

from .models import (
    Category,
    Product,
    ProductInLot,
    LotCost,
    Lot,
    Warehouse,
    ProductInWarehouse,
    Consumer,
    Order,
    ProductInOrder,
    Cost,
)
from django.db.models import Exists, OuterRef


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = (
            'name',
            'retail_price',
            'weight',
            'description',
        )


class ProductInLotForm(forms.ModelForm):
    class Meta:
        model = ProductInLot
        fields = (
            'product',
            'quantity',
            'purchase_price',
            'description'
        )


class ProductInLotCreateForm(forms.ModelForm):
    selected_objects = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple)
    quantities = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple)
    purchase_prices = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple)
    descriptions = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = ProductInLot
        fields = ['selected_objects', 'quantities',
                  'purchase_prices', 'descriptions']


class LotCostForm(forms.ModelForm):
    class Meta:
        model = LotCost
        fields = ['name', 'amount_spent', 'distribution', 'description']


class LotForm(forms.ModelForm):

    # Добавить в форму надпись "Введите описание партии при необходимости"
    description = forms.CharField(
        label='Введите описание партии при необходимости',
        required=False,
        widget=forms.Textarea
    )

    class Meta:
        model = Lot
        fields = ['description']


class LotUpdateForm(forms.ModelForm):

    STATUS_CHOICES = [
        ('paid', 'оплачен'),
        ('delivered', 'доставлен'),
    ]

    status = forms.ChoiceField(
        label='Статус партии',
        choices=STATUS_CHOICES,
        required=False,
    )

    class Meta:
        model = Lot
        fields = '__all__'


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = '__all__'


class ProductInWarehouseForm(forms.ModelForm):
    class Meta:
        model = ProductInWarehouse
        exclude = ['warehouse']


class ConsumerForm(forms.ModelForm):
    class Meta:
        model = Consumer
        exclude = ['total_cost', 'level']


class OrderForm(forms.ModelForm):

    STATUS_CHOICES = [
        ('new', 'новый'),
        ('paid', 'оплачен'),
        ('shipped', 'отгружен'),
    ]

    status = forms.ChoiceField(
        label='Статус заказа',
        choices=STATUS_CHOICES,
        required=False,
    )

    class Meta:
        model = Order
        exclude = ['consumer', 'warehouse']


class OrderUpdateForm(forms.ModelForm):

    STATUS_CHOICES = [
        ('paid', 'оплачен'),
        ('shipped', 'отгружен'),
    ]

    status = forms.ChoiceField(
        label='Статус заказа',
        choices=STATUS_CHOICES,
        required=False,
    )

    class Meta:
        model = Order
        exclude = ['consumer', 'warehouse']


class ProductInOrderForm(forms.ModelForm):
    available_products = Product.objects.filter(
        productinwarehouse__isnull=False).distinct()

    product = forms.ModelChoiceField(
        queryset=available_products,
        label='Товары на складе',
    )

    class Meta:
        model = ProductInOrder
        exclude = ['order']


class CostForm(forms.ModelForm):
    date_created = forms.DateField(
        label='Дата',
        widget=forms.DateInput(
            attrs={'class': 'datepicker', 'readonly': 'readonly'},
        ),
    )

    class Meta:
        model = Cost
        fields = '__all__'



class BalanceForm(forms.Form):
    current_date = now().date()  # Получить текущую дату
    first_day_of_month = date(current_date.year, current_date.month, 1)
    date_from = forms.DateField(
        label='Дата начала периода',
        initial=first_day_of_month,
    )
    date_to = forms.DateField(
        label='Дата конца периода',
        initial=current_date,
    )