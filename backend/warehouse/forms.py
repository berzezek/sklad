from django import forms

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
    Debit,
    Credit,
    Balance,
)


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
        exclude = [ 'lot' ]


class LotCostForm(forms.ModelForm):
    class Meta:
        model = LotCost
        exclude = [ 'lot' ]


class LotForm(forms.ModelForm):
    class Meta:
        model = Lot
        fields = [ 'description' ]


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = '__all__'


class ProductInWarehouseForm(forms.ModelForm):
    class Meta:
        model = ProductInWarehouse
        exclude = [ 'warehouse' ]


class ConsumerForm(forms.ModelForm):
    class Meta:
        model = Consumer
        exclude = [ 'total_cost', 'level' ]


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = '__all__'


class ProductInOrderForm(forms.ModelForm):
    class Meta:
        model = ProductInOrder
        exclude = [ 'order' ]


class DebitForm(forms.ModelForm):
    class Meta:
        model = Debit
        fields = '__all__'


class CreditForm(forms.ModelForm):
    class Meta:
        model = Credit
        fields = '__all__'


class BalanceForm(forms.ModelForm):
    class Meta:
        model = Balance
        fields = '__all__'
