import csv
from datetime import date
from urllib.parse import quote
from django.db.models import Q

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
    LotCostForm,
    LotForm,
    WarehouseForm,
    ProductInWarehouseForm,
    ConsumerForm,
    OrderForm,
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


class CategoryCreateView(CreateView):
    model = Category
    template_name = 'warehouse/category/category_create.html'
    form_class = CategoryForm
    success_url = reverse_lazy('warehouse:category_list')


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'warehouse/category/category_detail.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product_list = Product.objects.filter(category=self.kwargs['pk'])
        
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

        context['product_list'] = page_obj
        context['search_query'] = search_query  # Передаем поисковой запрос в контекст
        return context

    def render_to_response(self, context, **response_kwargs):
        if 'format' in self.request.GET and self.request.GET[ 'format' ] == 'csv':

            filename = f'Справочник продуктов от {now().strftime("%Y-%m-%d")}.csv'
            response = HttpResponse(content_type='text/csv')
            response[ 'Content-Disposition' ] = f'attachment; filename*=UTF-8\'\'{quote(filename)}'

            writer = csv.writer(response)
            writer.writerow([ "#", "Наименование", "Розничная цена", "Вес кг." ])

            products = context[ 'product_list' ]
            for product in products:
                writer.writerow([ product.id, product.name, product.retail_price, product.weight ])
            writer.writerow([ ])  # Пустая строка
            writer.writerow([ '', 'Ответственный', '______', '______' ])
            writer.writerow([ '', 'Принял', '______', '______' ])
            return response
        return super().render_to_response(context, **response_kwargs)


class CategoryUpdateView(UpdateView):
    model = Category
    template_name = 'warehouse/category/category_update.html'
    form_class = CategoryForm
    success_url = reverse_lazy('warehouse:category_list')


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'warehouse/category/category_delete.html'
    success_url = reverse_lazy('warehouse:category_list')


class ProductListView(ListView):
    model = Product
    template_name = 'warehouse/product/product_list.html'
    paginate_by = 3

    def get_queryset(self):
        return Product.objects.filter(category=self.kwargs[ 'category_id' ])


class ProductCreateView(CreateView):
    model = Product
    template_name = 'warehouse/product/product_create.html'
    form_class = ProductForm

    def get_success_url(self):
        return reverse_lazy('warehouse:category_detail', kwargs={'pk': self.kwargs[ 'category_id' ]})

    def form_valid(self, form):
        category_id = self.kwargs[ 'category_id' ]
        category = Category.objects.get(pk=category_id)
        form.instance.category = category
        return super().form_valid(form)


class ProductDetailView(DetailView):
    model = Product
    template_name = 'warehouse/product/product_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[ 'category_id' ] = self.object.category_id
        return context


class ProductUpdateView(UpdateView):
    model = Product
    template_name = 'warehouse/product/product_update.html'
    form_class = ProductForm

    def get_success_url(self):
        return reverse_lazy('warehouse:category_detail', kwargs={'pk': self.object.category_id})


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'warehouse/product/product_delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:category_detail', kwargs={'pk': self.object.category_id})


class ProductInLotListView(ListView):
    model = ProductInLot
    template_name = 'warehouse/productinlot/productinlot_list.html'

    def get_queryset(self):
        return ProductInLot.objects.filter(lot=self.kwargs[ 'lot_id' ])


class ProductInLotCreateView(CreateView):
    model = ProductInLot
    template_name = 'warehouse/productinlot/productinlot_create.html'
    form_class = ProductInLotForm

    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.kwargs[ 'lot_id' ]})

    def form_valid(self, form):
        lot_id = self.kwargs[ 'lot_id' ]
        lot = Lot.objects.get(pk=lot_id)
        form.instance.lot = lot
        return super().form_valid(form)


class ProductInLotDetailView(DetailView):
    model = ProductInLot
    template_name = 'warehouse/productinlot/productinlot_detail.html'

    def get_context_data(self, **kwargs):
        for i in self.object.history.all():
            print(i)
        context = super().get_context_data(**kwargs)
        context[ 'history' ] = self.object.history.all()
        return context


class ProductInLotDeleteView(DeleteView):
    model = ProductInLot
    template_name = 'warehouse/productinlot/productinlot_delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.object.lot.id})


class ProductInLotUpdateView(UpdateView):
    model = ProductInLot
    template_name = 'warehouse/productinlot/productinlot_update.html'
    form_class = ProductInLotForm

    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.object.lot_id})


class LotCostListView(ListView):
    model = LotCost
    template_name = 'warehouse/lotcost/lotcost_list.html'

    def get_queryset(self):
        return LotCost.objects.filter(lot=self.kwargs[ 'lot_id' ])


class LotCostCreateView(CreateView):
    model = LotCost
    template_name = 'warehouse/lotcost/lotcost_create.html'
    form_class = LotCostForm
    success_url = reverse_lazy('warehouse:lotcost_list')

    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.kwargs[ 'lot_id' ]})

    def form_valid(self, form):
        lot_id = self.kwargs[ 'lot_id' ]
        lot = Lot.objects.get(pk=lot_id)
        form.instance.lot = lot
        return super().form_valid(form)


class LotCostDetailView(DetailView):
    model = LotCost
    template_name = 'warehouse/lotcost/lotcost_detail.html'


class LotCostUpdateView(UpdateView):
    model = LotCost
    template_name = 'warehouse/lotcost/lotcost_update.html'
    form_class = LotCostForm

    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.object.lot.id})


class LotCostDeleteView(DeleteView):
    model = LotCost
    template_name = 'warehouse/lotcost/lotcost_delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:lot_detail', kwargs={'pk': self.object.lot.id})


class LotListView(ListView):
    model = Lot
    template_name = 'warehouse/lot/lot_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        excluded_lot_costs = [ ]
        for lot in context[ 'object_list' ]:
            if lot.status == 'paid':
                existing_costs_out = Cost.objects.filter(Q(name__startswith=f'Затраты {lot.pk} на лот')
                                                       | Q(name__startswith=f'Оплата лота {lot.pk}'))

                existing_cost_out_names = [ cost_out.name for cost_out in existing_costs_out ]

                lot_costs = lot.lotcost_set.exclude(name__in=existing_cost_out_names)

                excluded_lot_costs.extend(lot_costs)

        context[ 'excluded_lot_costs' ] = excluded_lot_costs

        return context


class LotCreateView(CreateView):
    model = Lot
    form_class = LotForm
    template_name = 'warehouse/lot/lot_create.html'
    success_url = reverse_lazy('warehouse:lot_list')


class LotDetailView(DetailView):
    model = Lot
    template_name = 'warehouse/lot/lot_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[ 'productinlot_list' ] = ProductInLot.objects.filter(lot=self.object)
        context[ 'lotcost_list' ] = LotCost.objects.filter(lot=self.object)
        context[ 'history' ] = self.object.history.all()[ ::-1 ]
        return context

    def render_to_response(self, context, **response_kwargs):
        if 'format' in self.request.GET and self.request.GET[ 'format' ] == 'csv':
            filename = f'Лот_{self.object.pk}_от_{now().strftime("%Y-%m-%d")}.csv'
            response = HttpResponse(content_type='text/csv')
            response[ 'Content-Disposition' ] = f'attachment; filename*=UTF-8\'\'{quote(filename)}'

            writer = csv.writer(response)
            writer.writerow([ "", "Список продуктов в лоте" ])
            writer.writerow([ "#", "Наименование товара", "Количество", "Стоимость" ])

            productinlot_list = context[ 'productinlot_list' ]
            for productinlot in productinlot_list:
                writer.writerow(
                    [ productinlot.pk, productinlot.product.name, productinlot.quantity, productinlot.purchase_price ])

            writer.writerow([ ])
            writer.writerow([ "", "Список расходов по лоту" ])
            writer.writerow([ "#", "Наименование расхода", "Стоимость", "Дата" ])
            lotcost_list = context[ 'lotcost_list' ]
            for lotcost in lotcost_list:
                writer.writerow([ lotcost.pk, lotcost.get_display_name, lotcost.amount_spent, lotcost.date ])

            writer.writerow([ ])
            writer.writerow([ "", "История изменений статуса лота" ])
            writer.writerow([ "#", "Статус", "Дата" ])
            history = context[ 'history' ]
            for i in history:
                writer.writerow([ i.pk, i.get_status_display, i.date ])

            return response

        return super().render_to_response(context, **response_kwargs)


class LotUpdateView(UpdateView):
    model = Lot
    template_name = 'warehouse/lot/lot_update.html'
    fields = '__all__'
    success_url = reverse_lazy('warehouse:lot_list')

    def form_valid(self, form):
        if form.instance.history.first().status == 'delivered':
            form.add_error(None, 'Нельзя изменить лот, который уже доставлен')
            return super().form_invalid(form)
        elif form.instance.history.first().status == 'paid':
            if form.instance.status == 'paid':
                add_costs_out_from_lot_if_not_exists(form.instance)
        if form.instance.history.first().status == 'delivered_to_warehouse':
            form.add_error(None, 'Нельзя изменить лот, который уже находится на складе')
            return super().form_invalid(form)
        return super().form_valid(form)


class LotDeleteView(DeleteView):
    model = Lot
    template_name = 'warehouse/lot/lot_delete.html'
    success_url = reverse_lazy('warehouse:lot_list')


class WarehouseListView(ListView):
    model = Warehouse
    template_name = 'warehouse/warehouse/warehouse_list.html'


class WarehouseCreateView(CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'warehouse/warehouse/warehouse_create.html'
    success_url = reverse_lazy('warehouse:warehouse_list')


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
            .order_by('-date')[ :1 ]
            .values('cost_price')
        )

        last_date_subquery = (
            ProductInWarehouse.objects
            .filter(warehouse=self.object)
            .filter(product_id=OuterRef('product_id'))
            .order_by('-date')[ :1 ]
            .values('date')
        )

        product_in_warehouse = (
            ProductInWarehouse.objects
            .filter(warehouse=self.object)
            .values('product')
            .annotate(
                product_name=F('product__name'),  # Отображение имени продукта
                retail_price=F('product__retail_price'),  # Отображение розничной цены
                total_quantity=Sum(
                    Case(
                        When(transaction__in=[ 'in', 'return' ], then=F('quantity')),
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
        context[ 'productinwarehouse_all_list' ] = product_in_warehouse_all
        context[ 'productinwarehouse_list' ] = product_in_warehouse
        context[ 'delivered_lot_list' ] = delivered_lot_list
        return context


class WarehouseUpdateView(UpdateView):
    model = Warehouse
    template_name = 'warehouse/warehouse/warehouse_update.html'
    fields = '__all__'
    success_url = reverse_lazy('warehouse:warehouse_list')


class WarehouseDeleteView(DeleteView):
    model = Warehouse
    template_name = 'warehouse/warehouse/warehouse_delete.html'
    success_url = reverse_lazy('warehouse:warehouse_list')


class ProductInWarehouseListView(ListView):
    model = ProductInWarehouse
    template_name = 'warehouse/productinwarehouse/productinwarehouse_list.html'

    def get_queryset(self):
        return ProductInWarehouse.objects.filter(warehouse=self.kwargs[ 'warehouse_id' ])


class ProductInWarehouseBalancedListView(ListView):
    model = ProductInWarehouse
    template_name = 'warehouse/productinwarehouse/productinwarehouse_balanced_list.html'

    def get_queryset(self):
        last_cost_price_subquery = (
            ProductInWarehouse.objects
            .filter(product_id=OuterRef('product_id'), warehouse_id=OuterRef('warehouse_id'))
            .order_by('-date')[ :1 ]
            .values('cost_price')
        )

        last_date_subquery = (
            ProductInWarehouse.objects
            .filter(product_id=OuterRef('product_id'), warehouse_id=OuterRef('warehouse_id'))
            .order_by('-date')[ :1 ]
            .values('date')
        )

        product_in_warehouse = (
            ProductInWarehouse.objects
            .values('product', 'warehouse')
            .annotate(
                total_quantity=Sum(
                    Case(
                        When(transaction__in=[ 'in', 'return' ], then=F('quantity')),
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
    template_name = 'warehouse/productinwarehouse/productinwarehouse_create.html'
    success_url = reverse_lazy('warehouse:productinwarehouse_list')

    def get_success_url(self):
        return reverse_lazy('warehouse:warehouse_detail', kwargs={'pk': self.kwargs[ 'warehouse_id' ]})

    def form_valid(self, form):
        warehouse_id = self.kwargs[ 'warehouse_id' ]
        warehouse = Warehouse.objects.get(pk=warehouse_id)
        form.instance.warehouse = warehouse
        return super().form_valid(form)


class ProductInWarehouseDetailView(DetailView):
    model = ProductInWarehouse
    template_name = 'warehouse/productinwarehouse/productinwarehouse_detail.html'


class ProductInWarehouseUpdateView(UpdateView):
    model = ProductInWarehouse
    template_name = 'warehouse/productinwarehouse/productinwarehouse_update.html'
    form_class = ProductInWarehouseForm

    def get_success_url(self):
        return reverse_lazy('warehouse:warehouse_detail', kwargs={'pk': self.kwargs[ 'warehouse_id' ]})


class ProductInWarehouseDeleteView(DeleteView):
    model = ProductInWarehouse
    template_name = 'warehouse/productinwarehouse/productinwarehouse_delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:warehouse_detail', kwargs={'pk': self.object.warehouse.id})


class ConsumerListView(ListView):
    model = Consumer
    template_name = 'warehouse/consumer/consumer_list.html'


class ConsumerCreateView(CreateView):
    model = Consumer
    form_class = ConsumerForm
    template_name = 'warehouse/consumer/consumer_create.html'
    success_url = reverse_lazy('warehouse:consumer_list')


class ConsumerDetailView(DetailView):
    model = Consumer
    template_name = 'warehouse/consumer/consumer_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[ 'order_list' ] = Order.objects.filter(consumer=self.object.pk)
        return context


class ConsumerUpdateView(UpdateView):
    model = Consumer
    template_name = 'warehouse/consumer/consumer_update.html'
    form_class = ConsumerForm
    success_url = reverse_lazy('warehouse:consumer_list')


class ConsumerDeleteView(DeleteView):
    model = Consumer
    template_name = 'warehouse/consumer/consumer_delete.html'
    success_url = reverse_lazy('warehouse:consumer_list')


class OrderListView(ListView):
    model = Order
    template_name = 'warehouse/order/order_list.html'


class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'warehouse/order/order_create.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:consumer_detail', kwargs={'pk': self.kwargs[ 'consumer_id' ]})

    def form_valid(self, form):
        consumer_id = self.kwargs[ 'consumer_id' ]
        consumer = Consumer.objects.get(pk=consumer_id)
        form.instance.consumer = consumer
        return super().form_valid(form)


class OrderDetailView(DetailView):
    model = Order
    template_name = 'warehouse/order/order_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context[ 'productinorder_list' ] = ProductInOrder.objects.filter(order=self.object)
        return context


class OrderUpdateView(UpdateView):
    model = Order
    template_name = 'warehouse/order/order_update.html'
    form_class = OrderForm

    def get_success_url(self):
        return reverse_lazy('warehouse:consumer_detail', kwargs={'pk': self.object.consumer.id})

    def form_valid(self, form):
        if form.instance.history.first().status == 'shipped':
            # сообщение в форме об ошибке
            form.add_error(None, 'Нельзя изменить заказ, который уже отправлен')
            return super().form_invalid(form)
        elif form.instance.history.first().status == 'paid':
            if form.instance.status == 'paid':
                # сообщение в форме об ошибке
                form.add_error(None, 'Нельзя изменить статус заказа на "оплачен", т.к. он уже оплачен')
                return super().form_invalid(form)
        return super().form_valid(form)


class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'warehouse/order/order_delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:consumer_detail', kwargs={'pk': self.object.consumer.id})


class ProductInOrderListView(ListView):
    model = ProductInOrder
    template_name = 'warehouse/productinorder/productinorder_list.html'

    def get_queryset(self):
        return ProductInOrder.objects.filter(order=self.kwargs[ 'order_id' ])


class ProductInOrderCreateView(CreateView):
    model = ProductInOrder
    form_class = ProductInOrderForm
    template_name = 'warehouse/productinorder/productinorder_create.html'
    success_url = reverse_lazy('warehouse:productinorder_list')

    def get_success_url(self):
        return reverse_lazy('warehouse:order_detail', kwargs={'pk': self.object.order.pk})

    def form_valid(self, form):
        order_id = self.kwargs[ 'order_id' ]
        order = Order.objects.get(pk=order_id)
        form.instance.order = order
        return super().form_valid(form)


class ProductInOrderDetailView(DetailView):
    model = ProductInOrder
    template_name = 'warehouse/productinorder/productinorder_detail.html'


class ProductInOrderUpdateView(UpdateView):
    model = ProductInOrder
    template_name = 'warehouse/productinorder/productinorder_update.html'
    form_class = ProductInOrderForm

    def get_success_url(self):
        return reverse_lazy('warehouse:order_detail', kwargs={'pk': self.kwargs[ 'order_id' ]})


class ProductInOrderDeleteView(DeleteView):
    model = ProductInOrder
    template_name = 'warehouse/productinorder/productinorder_delete.html'

    def get_success_url(self):
        return reverse_lazy('warehouse:order_detail', kwargs={'pk': self.kwargs[ 'order_id' ]})
    

class CostListView(ListView):
    model = Cost
    template_name = 'warehouse/cost/cost_list.html'


class CostCreateView(CreateView):
    model = Cost
    form_class = CostForm
    template_name = 'warehouse/cost/cost_create.html'
    success_url = reverse_lazy('warehouse:balance_list')


class CostDetailView(DetailView):
    model = Cost
    template_name = 'warehouse/cost/cost_detail.html'


class CostUpdateView(UpdateView):
    model = Cost
    template_name = 'warehouse/cost/cost_update.html'
    form_class = CostForm
    success_url = reverse_lazy('warehouse:balance_list')


class CostDeleteView(DeleteView):
    model = Cost
    template_name = 'warehouse/cost/cost_delete.html'
    success_url = reverse_lazy('warehouse:balance_list')



def get_balance_by_date(request):
    form = BalanceForm()
    costs_in = None
    costs_out = None
    balance = None
    costs_in_all = Cost.objects.filter(transaction='in')
    costs_out_all = Cost.objects.filter(transaction='out')
    balance_all = (costs_in_all.aggregate(Sum('amount'))[ 'amount__sum' ] or 0) - (
            costs_out_all.aggregate(Sum('amount'))[ 'amount__sum' ] or 0)

    if request.method == 'GET':
        today = date.today()
        start_of_month = date(today.year, today.month, 1)
        costs_in = Cost.objects.filter(date__gte=start_of_month, transaction='in')
        costs_out = Cost.objects.filter(date__gte=start_of_month, transaction='out')
        balance = (costs_in.aggregate(Sum('amount'))[ 'amount__sum' ] or 0) - (
                costs_out.aggregate(Sum('amount'))[ 'amount__sum' ] or 0)

    elif request.method == 'POST':
        form = BalanceForm(request.POST)

        if form.is_valid():
            date_from = form.cleaned_data[ 'date_from' ]
            date_to = form.cleaned_data[ 'date_to' ]
            costs_in = Cost.objects.filter(date__gte=date_from, date__lte=date_to, transaction='in')
            costs_out = Cost.objects.filter(date__gte=date_from, date__lte=date_to, transaction='out')
            balance = (costs_in.aggregate(Sum('amount'))[ 'amount__sum' ] or 0) - (
                    costs_out.aggregate(Sum('amount'))[ 'amount__sum' ] or 0)

    return render(request, 'warehouse/balance/balance_list.html', {
        'form': form,
        'costs_in': costs_in,
        'costs_out': costs_out,
        'balance': balance,
        'balance_all': balance_all,
    })
