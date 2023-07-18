import csv
from datetime import date
from typing import Any, Dict
from urllib.parse import quote
from django import http
from django.db.models import Q
from django.shortcuts import redirect
from django.contrib import messages

from django.db.models import Sum, F, Subquery, OuterRef, Case, When, Q
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils.timezone import now
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from django.core.paginator import Paginator

from .forms import (
    CategoryForm,
    ProductForm,
    ProductInLotForm,
    ProductInLotCreateForm,
    LotCostForm,
    LotForm,
    LotUpdateForm,
    WarehouseForm,
    ProductInWarehouseForm,
    ConsumerForm,
    OrderForm,
    OrderUpdateForm,
    ProductInOrderForm,
    BalanceForm,
    CostForm,
)

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
from .utils import add_costs_out_from_lot_if_not_exists


def index(request):
    return render(request, 'warehouse/index.html')


class CategoryListView(ListView):
    model = Category
    template_name = 'warehouse/category/category_list.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['columns'] = ['#', 'Наименование', 'Описание']
        kwargs['columns_attributes'] = ['pk', 'name', 'description']
        return super().get_context_data(**kwargs)
    
    def render_to_response(self, context: Dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if 'format' in self.request.GET and self.request.GET['format'] == 'csv':
            filename = f'Справочник Товаров от {now().strftime("%Y-%m-%d")}.csv'
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{quote(filename)}'

            writer = csv.writer(response)
            writer.writerow(["#", "Наименование", "Розничная цена", "Вес кг."])

            products = Product.objects.all()
            for product in products:
                writer.writerow([product.id, product.name,
                                product.retail_price, product.weight])
            writer.writerow([])  # Пустая строка
            writer.writerow(['', 'Ответственный', '______', '______'])
            writer.writerow(['', 'Принял', '______', '______'])
            return response
        
        return super().render_to_response(context, **response_kwargs)


class CategoryCreateView(CreateView):
    model = Category
    template_name = 'includes/create.html'
    form_class = CategoryForm
    success_url = reverse_lazy('warehouse:category_list')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['title'] = 'новую категорию'
        return super().get_context_data(**kwargs)
    

class CategoryDetailView(DetailView):
    model = Category
    template_name = 'warehouse/category/category_detail.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_list = Product.objects.filter(category=self.kwargs['pk']).order_by('id')

        # Получаем параметр поиска из GET-запроса
        search_query = self.request.GET.get('q')
        if search_query:
            # Фильтруем список продуктов по поисковому запросу
            product_list = product_list.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        paginator = Paginator(product_list, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['product_list'] = product_list
        context['page_obj'] = page_obj        # Передаем поисковой запрос в контекст
        context['search_query'] = search_query
        return context


class CategoryUpdateView(UpdateView):
    model = Category
    template_name = 'includes/update.html'
    form_class = CategoryForm
    success_url = reverse_lazy('warehouse:category_list')


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'includes/delete.html'
    success_url = reverse_lazy('warehouse:category_list')

    # Нельзя удалить категорию, если в ней есть продукты, или выдавать ошибку
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.product_set.count() > 0:
            return render(request, 'includes/delete_error.html', {
                'object': self.object,
                'error_message': 'Нельзя удалить категорию, в которой есть продукты'
                })
        return super().delete(request, *args, **kwargs)


class ProductListView(ListView):
    model = Product
    template_name = 'warehouse/product/product_list.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['columns'] = ['#', 'Наименование', 'Розничная цена', 'Вес кг.', 'Описание']
        kwargs['columns_attributes'] = ['pk', 'name', 'retail_price', 'weight', 'description']
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        return Product.objects.filter(category=self.kwargs['category_id'])


class ProductCreateView(CreateView):
    model = Product
    template_name = 'includes/create.html'
    form_class = ProductForm

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['title'] = 'новый продукт'
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('warehouse:category_detail', kwargs={'pk': self.kwargs['category_id']})

    def form_valid(self, form):
        category_id = self.kwargs['category_id']
        category = Category.objects.get(pk=category_id)
        form.instance.category = category
        return super().form_valid(form)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'warehouse/product/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_id'] = self.object.category_id
        return context


class ProductUpdateView(UpdateView):
    model = Product
    template_name = 'includes/update.html'
    form_class = ProductForm

    def get_success_url(self):
        return reverse_lazy('warehouse:category_detail', kwargs={'pk': self.object.category_id})


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'includes/delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:category_detail', kwargs={'pk': self.object.category_id})


class ProductInLotListView(ListView):
    model = ProductInLot
    template_name = 'warehouse/productinlot/productinlot_list.html'

    def get_queryset(self):
        return ProductInLot.objects.filter(lot=self.kwargs['lot_id'])


class ProductInLotCreateView(CreateView):
    model = ProductInLot
    template_name = 'includes/create_list.html'
    form_class = ProductInLotCreateForm

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['title'] = 'продукты в лот'
        product_list = Product.objects.all()
        
        search_query = self.request.GET.get('q')
        if search_query:
            # Фильтруем список продуктов по поисковому запросу
            product_list = product_list.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        kwargs['product_list'] = product_list
        kwargs['lot_id'] = self.kwargs['lot_id']
        return super().get_context_data(**kwargs)
        
    
    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.kwargs['lot_id']})
    
    def post(self, request, *args, **kwargs):
        object_ids = self.request.POST.getlist('selected_objects')
        quantities = self.request.POST.getlist('quantities')
        purchase_prices = self.request.POST.getlist('purchase_prices')
        descriptions = self.request.POST.getlist('descriptions')
        lot_id = self.kwargs['lot_id']
        lot = Lot.objects.get(pk=lot_id)

        if request.method == 'POST':
            message_text = ''
            for object_id, quantity, purchase_price, description in zip(object_ids, quantities, purchase_prices, descriptions):
                if quantity != '0' and purchase_price != '0':
                    try: 
                        product = Product.objects.get(pk=object_id)
                        product_in_lot = ProductInLot(product=product, lot=lot, quantity=int(quantity), purchase_price=float(purchase_price), description=description)
                        product_in_lot.save()
                        message_text += f'Продукт {product.name} в количестве {quantity} добавлен\n'
                    except:
                        message_text += f'!!! Внимание: Продукт {product.name} не добавлен\n'
            messages.success(request, message_text)
        return super().post(request, *args, **kwargs)


class ProductInLotDetailView(DetailView):
    model = ProductInLot
    template_name = 'warehouse/productinlot/productinlot_detail.html'

    def get_context_data(self, **kwargs):
        for i in self.object.history.all():
            print(i)
        context = super().get_context_data(**kwargs)
        context['history'] = self.object.history.all()
        return context


class ProductInLotDeleteView(DeleteView):
    model = ProductInLot
    template_name = 'includes/delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.object.lot.id})


class ProductInLotUpdateView(UpdateView):
    model = ProductInLot
    template_name = 'includes/update.html'
    form_class = ProductInLotForm

    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.object.lot_id})


class LotCostListView(ListView):
    model = LotCost
    template_name = 'warehouse/lotcost/lotcost_list.html'

    def get_queryset(self):
        return LotCost.objects.filter(lot=self.kwargs['lot_id'])


class LotCostCreateView(CreateView):
    model = LotCost
    template_name = 'includes/create.html'
    form_class = LotCostForm
    success_url = reverse_lazy('warehouse:lotcost_list')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['title'] = 'новый расход по лоту'
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.kwargs['lot_id']})

    def form_valid(self, form):
        lot_id = self.kwargs['lot_id']
        lot = Lot.objects.get(pk=lot_id)
        form.instance.lot = lot
        return super().form_valid(form)


class LotCostDetailView(DetailView):
    model = LotCost
    template_name = 'warehouse/lotcost/lotcost_detail.html'


class LotCostUpdateView(UpdateView):
    model = LotCost
    template_name = 'includes/update.html'
    form_class = LotCostForm

    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.object.lot.id})


class LotCostDeleteView(DeleteView):
    model = LotCost
    template_name = 'includes/delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.object.lot.id})


class LotListView(ListView):
    model = Lot
    template_name = 'warehouse/lot/lot_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        excluded_lot_costs = []
        for lot in context['object_list']:
            if lot.status == 'paid':
                existing_costs_out = Cost.objects.filter(Q(name__startswith=f'Затраты {lot.pk} на лот')
                                                         | Q(name__startswith=f'Оплата лота {lot.pk}'))

                existing_cost_out_names = [
                    cost_out.name for cost_out in existing_costs_out]

                lot_costs = lot.lotcost_set.exclude(
                    name__in=existing_cost_out_names)

                excluded_lot_costs.extend(lot_costs)

        context['excluded_lot_costs'] = excluded_lot_costs
        context['columns'] = ['#', 'Дата создания', 'Статус', 'Описание']
        context['columns_attributes'] = ['pk', 'date', 'status', 'description']
        return context


class LotCreateView(CreateView):
    model = Lot
    form_class = LotForm
    template_name = 'includes/create.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['title'] = 'новый лот'
        return super().get_context_data(**kwargs)
    
    def get_success_url(self):
        pk = self.object.pk
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': pk})


class LotDetailView(DetailView):
    model = Lot
    template_name = 'warehouse/lot/lot_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # количество продуктов в лоте поштучно
        product_in_lot_amount_count = ProductInLot.objects.filter(lot=self.object).aggregate(Sum('quantity')).get('quantity__sum')
        product_in_lot_list = ProductInLot.objects.filter(lot=self.object).select_related('product')
        product_in_lot_list = list(product_in_lot_list)

        lot_cost_queryset = LotCost.objects.filter(lot=self.object)


        for product_in_lot in product_in_lot_list:
            product_in_lot.cost_price = product_in_lot.purchase_price

            lot_cost = lot_cost_queryset
            
            if lot_cost_queryset.exists():
                lot_cost_amount_spent_equal = lot_cost.filter(distribution='equal').aggregate(Sum('amount_spent')).get('amount_spent__sum')
                lot_cost_amount_spent_by_weight = lot_cost.filter(distribution='by_weight').aggregate(Sum('amount_spent')).get('amount_spent__sum')
                lot_cost_amount_spent_by_price = lot_cost.filter(distribution='by_price').aggregate(Sum('amount_spent')).get('amount_spent__sum')

                product_in_lot_count = len(product_in_lot_list)

                if product_in_lot_count and lot_cost_amount_spent_equal:
                    product_in_lot.cost_price += lot_cost_amount_spent_equal / product_in_lot_amount_count

                if self.object.get_products_weight() and lot_cost_amount_spent_by_weight:
                    product_in_lot.cost_price += (lot_cost_amount_spent_by_weight / self.object.get_products_weight()) * product_in_lot.product.weight

                if self.object.get_total_lot_purchase_price() and lot_cost_amount_spent_by_price:
                    product_in_lot.cost_price += (lot_cost_amount_spent_by_price / self.object.get_total_lot_purchase_price()) * product_in_lot.purchase_price

        context['productinlot_list'] = product_in_lot_list
        context['lotcost_list'] = lot_cost_queryset
        context['history'] = self.object.history.all()[::-1]
        return context

    def render_to_response(self, context, **response_kwargs):
        if 'format' in self.request.GET and self.request.GET['format'] == 'csv':
            filename = f'Лот_{self.object.pk}_от_{now().strftime("%Y-%m-%d")}.csv'
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{quote(filename)}'

            writer = csv.writer(response)
            writer.writerow(["", "Список продуктов в лоте"])
            writer.writerow(["#", "Наименование товара", "Количество", "Вес кг.", "Закупочная стоимость", "Розничная цена"])

            productinlot_list = context['productinlot_list']
            for productinlot in productinlot_list:
                writer.writerow(
                    [productinlot.pk, productinlot.product.name, productinlot.quantity,productinlot.product.weight, productinlot.purchase_price, productinlot.product.retail_price])
            writer.writerow([])
            writer.writerow(["", "Сумма закупочной стоимости", self.object.get_total_lot_purchase_price()])
            writer.writerow([])
            writer.writerow(["", "Вес заказа кг.", self.object.get_products_weight()])
            writer.writerow([])
            writer.writerow([])
            writer.writerow(["", "Список расходов по лоту"])
            writer.writerow(["#", "Наименование расхода", "Сумма", "Дата"])
            lotcost_list = context['lotcost_list']
            for lotcost in lotcost_list:
                writer.writerow(
                    [lotcost.pk, lotcost.get_display_name(), lotcost.amount_spent, lotcost.date])
            writer.writerow([])
            writer.writerow(["", "Сумма расходов по лоту", self.object.get_total_lot_amount_spent()])
            writer.writerow([])
            writer.writerow(["", "Итоговая стоимость лота", self.object.get_total()])
            writer.writerow([])
            writer.writerow(["", "История изменений статуса лота"])
            writer.writerow(["#", "Статус", "Дата"])
            history = context['history']
            for i in history:
                writer.writerow([i.pk, i.get_status_display(), i.date])

            return response

        return super().render_to_response(context, **response_kwargs)


class LotUpdateView(UpdateView):
    model = Lot
    template_name = 'includes/update.html'
    # fields = '__all__'
    success_url = reverse_lazy('warehouse:lot_list')
    form_class = LotUpdateForm

    def form_valid(self, form):
        if form.instance.history.first().status == 'delivered':
            form.add_error(None, 'Нельзя изменить лот, который уже доставлен')
            return super().form_invalid(form)
        if form.instance.status == 'paid':
            add_costs_out_from_lot_if_not_exists(form.instance)
        if form.instance.history.first().status == 'delivered_to_warehouse':
            form.add_error(
                None, 'Нельзя изменить лот, который уже находится на складе')
            return super().form_invalid(form)
        return super().form_valid(form)


class LotDeleteView(DeleteView):
    model = Lot
    template_name = 'includes/delete.html'
    success_url = reverse_lazy('warehouse:lot_list')


class WarehouseListView(ListView):
    model = Warehouse
    template_name = 'warehouse/warehouse/warehouse_list.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['columns'] = ['#', 'Наименование', 'Описание']
        kwargs['columns_attributes'] = ['pk', 'name', 'description']
        return super().get_context_data(**kwargs)


class WarehouseCreateView(CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'includes/create.html'
    success_url = reverse_lazy('warehouse:warehouse_list')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['title'] = 'новый склад'
        return super().get_context_data(**kwargs)


class WarehouseDetailView(DetailView):
    model = Warehouse
    template_name = 'warehouse/warehouse/warehouse_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        delivered_lot_list = Lot.objects.filter(status='delivered')

        last_cost_price_subquery = (
            ProductInWarehouse.objects
            .filter(warehouse=self.object)
            .filter(product_id=OuterRef('product_id'))
            .order_by('-date')[:1]
            .values('cost_price')
        )

        last_date_subquery = (
            ProductInWarehouse.objects
            .filter(warehouse=self.object)
            .filter(product_id=OuterRef('product_id'))
            .order_by('-date')[:1]
            .values('date')
        )

        product_in_warehouse = (
            ProductInWarehouse.objects
            .filter(warehouse=self.object)
            .values('product')
            .annotate(
                product_name=F('product__name'),  # Отображение имени продукта
                # Отображение розничной цены
                retail_price=F('product__retail_price'),
                total_quantity=Sum(
                    Case(
                        When(transaction__in=[
                             'in', 'return'], then=F('quantity')),
                        default=-F('quantity'),
                    )
                ),
                last_cost_price=Subquery(last_cost_price_subquery),
                last_date=Subquery(last_date_subquery),
            )
        )

        product_in_warehouse_all = ProductInWarehouse.objects.filter(
            warehouse=self.object,
            transaction='in'
        ).order_by('product__name')
        context['productinwarehouse_all_list'] = product_in_warehouse_all
        context['productinwarehouse_list'] = product_in_warehouse
        context['delivered_lot_list'] = delivered_lot_list
        return context


class WarehouseUpdateView(UpdateView):
    model = Warehouse
    template_name = 'includes/update.html'
    fields = '__all__'
    success_url = reverse_lazy('warehouse:warehouse_list')


class WarehouseDeleteView(DeleteView):
    model = Warehouse
    template_name = 'includes/delete.html'
    success_url = reverse_lazy('warehouse:warehouse_list')


class ProductInWarehouseListView(ListView):
    model = ProductInWarehouse
    template_name = 'warehouse/productinwarehouse/productinwarehouse_list.html'

    def get_queryset(self):
        return ProductInWarehouse.objects.filter(warehouse=self.kwargs['warehouse_id'])


class ProductInWarehouseBalancedListView(ListView):
    model = ProductInWarehouse
    template_name = 'warehouse/productinwarehouse/productinwarehouse_balanced_list.html'

    def get_queryset(self):
        last_cost_price_subquery = (
            ProductInWarehouse.objects
            .filter(product_id=OuterRef('product_id'), warehouse_id=OuterRef('warehouse_id'))
            .order_by('-date')[:1]
            .values('cost_price')
        )

        last_date_subquery = (
            ProductInWarehouse.objects
            .filter(product_id=OuterRef('product_id'), warehouse_id=OuterRef('warehouse_id'))
            .order_by('-date')[:1]
            .values('date')
        )

        product_in_warehouse = (
            ProductInWarehouse.objects
            .values('product', 'warehouse')
            .annotate(
                total_quantity=Sum(
                    Case(
                        When(transaction__in=[
                             'in', 'return'], then=F('quantity')),
                        default=-F('quantity'),
                    )
                ),
                last_cost_price=Subquery(last_cost_price_subquery),
                last_date=Subquery(last_date_subquery),
            )
        )


class ProductInWarehouseCreateView(CreateView):
    model = ProductInWarehouse
    form_class = ProductInWarehouseForm
    template_name = 'includes/create.html'
    success_url = reverse_lazy('warehouse:productinwarehouse_list')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['title'] = 'новый продукт на складе'
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('warehouse:warehouse_detail', kwargs={'pk': self.kwargs['warehouse_id']})

    def form_valid(self, form):
        warehouse_id = self.kwargs['warehouse_id']
        warehouse = Warehouse.objects.get(pk=warehouse_id)
        form.instance.warehouse = warehouse
        return super().form_valid(form)


class ProductInWarehouseDetailView(DetailView):
    model = ProductInWarehouse
    template_name = 'warehouse/productinwarehouse/productinwarehouse_detail.html'


class ProductInWarehouseUpdateView(UpdateView):
    model = ProductInWarehouse
    template_name = 'includes/update.html'
    form_class = ProductInWarehouseForm

    def get_success_url(self):
        return reverse_lazy('warehouse:warehouse_detail', kwargs={'pk': self.kwargs['warehouse_id']})


class ProductInWarehouseDeleteView(DeleteView):
    model = ProductInWarehouse
    template_name = 'includes/delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:warehouse_detail', kwargs={'pk': self.object.warehouse.id})


class ConsumerListView(ListView):
    model = Consumer
    template_name = 'warehouse/consumer/consumer_list.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['columns'] = ['#', 'Наименование', 'Сумма покупок', 'Уровень покупателя', 'Описание']
        kwargs['columns_attributes'] = ['pk', 'name', 'total_cost', 'level', 'description']
        return super().get_context_data(**kwargs)


class ConsumerCreateView(CreateView):
    model = Consumer
    form_class = ConsumerForm
    template_name = 'includes/create.html'
    success_url = reverse_lazy('warehouse:consumer_list')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['title'] = 'нового покупателя'
        return super().get_context_data(**kwargs)


class ConsumerDetailView(DetailView):
    model = Consumer
    template_name = 'warehouse/consumer/consumer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Все неоплаченные заказы покупателя
        consumer_orders = Order.objects.filter(consumer=self.object.pk)
        not_paid_orders = []
        for order in consumer_orders:
            is_paid = False
            for i in order.history.all():
                # Если статус заказа никогда не был 'paid', то добавляем его в список
                if i.status == 'paid':
                    is_paid = True
                    break
            if not is_paid:
                not_paid_orders.append(order)
        context['not_paid_orders'] = not_paid_orders
        context['consumer_orders'] = consumer_orders
        return context


class ConsumerUpdateView(UpdateView):
    model = Consumer
    template_name = 'includes/update.html'
    form_class = ConsumerForm
    success_url = reverse_lazy('warehouse:consumer_list')


class ConsumerDeleteView(DeleteView):
    model = Consumer
    template_name = 'includes/delete.html'
    success_url = reverse_lazy('warehouse:consumer_list')


class OrderListView(ListView):
    model = Order
    template_name = 'warehouse/order/order_list.html'


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'includes/create.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['title'] = 'новый заказ'
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('warehouse:consumer_detail', kwargs={'pk': self.kwargs['consumer_id']})

    def form_valid(self, form):
        consumer_id = self.kwargs['consumer_id']
        consumer = Consumer.objects.get(pk=consumer_id)
        form.instance.consumer = consumer
        return super().form_valid(form)


class OrderDetailView(DetailView):
    model = Order
    template_name = 'warehouse/order/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productinorder_list'] = ProductInOrder.objects.filter(
            order=self.object)
        context['history'] = self.object.history.all()[::-1]
        return context
    
    def render_to_response(self, context: Dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if 'format' in self.request.GET and self.request.GET['format'] == 'csv':
            filename = f'Заказ_{self.object.pk}_от_{now().strftime("%Y-%m-%d")}.csv'
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{quote(filename)}'

            writer = csv.writer(response)
            writer.writerow(["", "Покупатель", self.object.consumer.name])
            writer.writerow(["", "Список продуктов в заказе"])
            writer.writerow(["#", "Наименование товара", "Количество", "Вес кг.", "Цена"])

            productinorder_list = context['productinorder_list']
            for productinorder in productinorder_list:
                writer.writerow(
                    [productinorder.pk, productinorder.product.name, productinorder.quantity,productinorder.product.weight, productinorder.purchase_price, productinorder.product.retail_price])
            writer.writerow([])
            writer.writerow(["", "Вес заказа кг.", self.object.get_total_order_weight()])
            writer.writerow([])
            writer.writerow(["", "Итоговая стоимость заказа", self.object.get_total_order_cost_price()])
            writer.writerow([])
            writer.writerow(["", "История изменений статуса заказа"])
            writer.writerow(["#", "Статус", "Дата"])
            history = context['history']
            for i in history:
                writer.writerow([i.pk, i.get_status_display(), i.date])

            return response

        return super().render_to_response(context, **response_kwargs)


class OrderUpdateView(UpdateView):
    model = Order
    template_name = 'includes/update.html'
    form_class = OrderUpdateForm

    def get_success_url(self):
        return reverse_lazy('warehouse:consumer_detail', kwargs={'pk': self.object.consumer.id})

    def form_valid(self, form):
        if form.instance.history.first().status == 'paid':
            if form.instance.status == 'paid':
                # сообщение в форме об ошибке
                form.add_error(
                    None, 'Нельзя изменить статус заказа на "оплачен", т.к. он уже оплачен')
                return super().form_invalid(form)
        if form.instance.status == 'shipped':
            if form.instance.history.first().status != 'paid':
                Order.objects.filter(pk=self.object.pk).update(
                    status='not_paid')
        return super().form_valid(form)


class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'includes/delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:consumer_detail', kwargs={'pk': self.object.consumer.id})


class ProductInOrderListView(ListView):
    model = ProductInOrder
    template_name = 'warehouse/productinorder/productinorder_list.html'

    def get_queryset(self):
        return ProductInOrder.objects.filter(order=self.kwargs['order_id'])


class ProductInOrderCreateView(CreateView):
    model = ProductInOrder
    form_class = ProductInOrderForm
    template_name = 'includes/create.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['title'] = 'новый продукт в заказ'
        return super().get_context_data(**kwargs)

    def get_success_url(self):
        return reverse_lazy('warehouse:order_detail', kwargs={'pk': self.object.order.pk})

    def form_valid(self, form):
        order_id = self.kwargs['order_id']
        order = Order.objects.get(pk=order_id)
        form.instance.order = order
        return super().form_valid(form)


class ProductInOrderDetailView(DetailView):
    model = ProductInOrder
    template_name = 'warehouse/productinorder/productinorder_detail.html'


class ProductInOrderUpdateView(UpdateView):
    model = ProductInOrder
    template_name = 'includes/update.html'
    form_class = ProductInOrderForm

    def get_success_url(self):
        return reverse_lazy('warehouse:order_detail', kwargs={'pk': self.kwargs['order_id']})


class ProductInOrderDeleteView(DeleteView):
    model = ProductInOrder
    template_name = 'includes/delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:order_detail', kwargs={'pk': self.kwargs['order_id']})


class CostListView(ListView):
    model = Cost
    template_name = 'warehouse/cost/cost_list.html'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['columns'] = ['#', 'Наименование', 'Сумма', 'Дата', 'Описание']
        kwargs['columns_attributes'] = ['pk', 'name', 'amount', 'date', 'description']
        return super().get_context_data(**kwargs)


class CostCreateView(CreateView):
    model = Cost
    form_class = CostForm
    template_name = 'includes/create.html'
    success_url = reverse_lazy('warehouse:balance_list')

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        kwargs['title'] = 'новый расход'
        return super().get_context_data(**kwargs)


class CostDetailView(DetailView):
    model = Cost
    template_name = 'warehouse/cost/cost_detail.html'


class CostUpdateView(UpdateView):
    model = Cost
    template_name = 'includes/update.html'
    form_class = CostForm
    success_url = reverse_lazy('warehouse:balance_list')


class CostDeleteView(DeleteView):
    model = Cost
    template_name = 'includes/delete.html'
    success_url = reverse_lazy('warehouse:balance_list')


def get_balance_by_date(request):
    form = BalanceForm()
    costs_in = None
    costs_out = None
    balance = None
    costs_in_all = Cost.objects.filter(transaction='in')
    costs_out_all = Cost.objects.filter(transaction='out')
    balance_all = (costs_in_all.aggregate(Sum('amount'))['amount__sum'] or 0) - (
        costs_out_all.aggregate(Sum('amount'))['amount__sum'] or 0)

    if request.method == 'GET':
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        costs_in = Cost.objects.filter(
            date__gte=start_of_month, transaction='in')
        costs_out = Cost.objects.filter(
            date__gte=start_of_month, transaction='out')
        balance = (costs_in.aggregate(Sum('amount'))['amount__sum'] or 0) - (
            costs_out.aggregate(Sum('amount'))['amount__sum'] or 0)

    elif request.method == 'POST':
        form = BalanceForm(request.POST)

        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            costs_in = Cost.objects.filter(
                date__gte=date_from, date__lte=date_to, transaction='in')
            costs_out = Cost.objects.filter(
                date__gte=date_from, date__lte=date_to, transaction='out')
            balance = (costs_in.aggregate(Sum('amount'))['amount__sum'] or 0) - (
                costs_out.aggregate(Sum('amount'))['amount__sum'] or 0)

    return render(request, 'warehouse/balance/balance_list.html', {
        'form': form,
        'costs_in': costs_in,
        'costs_out': costs_out,
        'balance': balance,
        'balance_all': balance_all,
    })
