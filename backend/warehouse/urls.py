from django.urls import path

from .services import (
    warehouse,
)
from .views import (
    index,

    CategoryListView,
    CategoryCreateView,
    CategoryDetailView,
    CategoryUpdateView,
    CategoryDeleteView,

    ProductListView,
    ProductCreateView,
    ProductDetailView,
    ProductUpdateView,
    ProductDeleteView,

    ProductInLotListView,
    ProductInLotCreateView,
    ProductInLotDetailView,
    ProductInLotUpdateView,
    ProductInLotDeleteView,

    LotCostListView,
    LotCostCreateView,
    LotCostDetailView,
    LotCostUpdateView,
    LotCostDeleteView,

    LotListView,
    LotCreateView,
    LotDetailView,
    LotUpdateView,
    LotDeleteView,

    WarehouseListView,
    WarehouseCreateView,
    WarehouseDetailView,
    WarehouseUpdateView,
    WarehouseDeleteView,

    ProductInWarehouseListView,
    ProductInWarehouseCreateView,
    ProductInWarehouseDetailView,
    ProductInWarehouseUpdateView,
    ProductInWarehouseDeleteView,

    ConsumerListView,
    ConsumerCreateView,
    ConsumerDetailView,
    ConsumerUpdateView,
    ConsumerDeleteView,

    OrderListView,
    OrderCreateView,
    OrderDetailView,
    OrderUpdateView,
    OrderDeleteView,

    ProductInOrderListView,
    ProductInOrderCreateView,
    ProductInOrderDetailView,
    ProductInOrderUpdateView,
    ProductInOrderDeleteView,

    DebitListView,
    DebitCreateView,
    DebitDetailView,
    DebitUpdateView,
    DebitDeleteView,

    CreditListView,
    CreditCreateView,
    CreditDetailView,
    CreditUpdateView,
    CreditDeleteView,

    BalanceListView,
    BalanceCreateView,
    BalanceDetailView,
    BalanceUpdateView,
    BalanceDeleteView,
)

app_name = 'warehouse'

urlpatterns = [
    path('', index, name='index'),

    path('category/list/', CategoryListView.as_view(), name='category_list'),
    path('category/create/', CategoryCreateView.as_view(), name='category_create'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='category_detail'),
    path('category/<int:pk>/update/', CategoryUpdateView.as_view(), name='category_update'),
    path('category/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),

    path('product/list/<int:category_id>/', ProductListView.as_view(), name='product_list'),
    path('product/<int:category_id>/create/', ProductCreateView.as_view(), name='product_create'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name='product_update'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='product_delete'),

    path('productinlot/list/<int:lot_id>/', ProductInLotListView.as_view(), name='productinlot_list'),
    path('productinlot/<int:lot_id>/create/', ProductInLotCreateView.as_view(), name='productinlot_create'),
    path('productinlot/<int:pk>/', ProductInLotDetailView.as_view(), name='productinlot_detail'),
    path('productinlot/<int:pk>/update/', ProductInLotUpdateView.as_view(), name='productinlot_update'),
    path('productinlot/<int:pk>/delete/', ProductInLotDeleteView.as_view(), name='productinlot_delete'),

    path('lotcost/list/<int:lot_id>/', LotCostListView.as_view(), name='lotcost_list'),
    path('lotcost/<int:lot_id>/create/', LotCostCreateView.as_view(), name='lotcost_create'),
    path('lotcost/<int:pk>/', LotCostDetailView.as_view(), name='lotcost_detail'),
    path('lotcost/<int:pk>/update/', LotCostUpdateView.as_view(), name='lotcost_update'),
    path('lotcost/<int:pk>/delete/', LotCostDeleteView.as_view(), name='lotcost_delete'),

    path('lot/list/', LotListView.as_view(), name='lot_list'),
    path('lot/create/', LotCreateView.as_view(), name='lot_create'),
    path('lot/<int:pk>/', LotDetailView.as_view(), name='lot_detail'),
    path('lot/<int:pk>/update/', LotUpdateView.as_view(), name='lot_update'),
    path('lot/<int:pk>/delete/', LotDeleteView.as_view(), name='lot_delete'),

    path('warehouse/list/', WarehouseListView.as_view(), name='warehouse_list'),
    path('warehouse/create/', WarehouseCreateView.as_view(), name='warehouse_create'),
    path('warehouse/<int:pk>/', WarehouseDetailView.as_view(), name='warehouse_detail'),
    path('warehouse/<int:pk>/update/', WarehouseUpdateView.as_view(), name='warehouse_update'),
    path('warehouse/<int:pk>/delete/', WarehouseDeleteView.as_view(), name='warehouse_delete'),

    path('productinwarehouse/list/<int:warehouse_id>/', ProductInWarehouseListView.as_view(),
         name='productinwarehouse_list'),
    path('productinwarehouse/<int:warehouse_id>/create/', ProductInWarehouseCreateView.as_view(),
         name='productinwarehouse_create'),
    path('productinwarehouse/<int:pk>/', ProductInWarehouseDetailView.as_view(), name='productinwarehouse_detail'),
    path('productinwarehouse/<int:pk>/update/', ProductInWarehouseUpdateView.as_view(),
         name='productinwarehouse_update'),
    path('productinwarehouse/<int:pk>/delete/', ProductInWarehouseDeleteView.as_view(),
         name='productinwarehouse_delete'),

    path('consumer/list/', ConsumerListView.as_view(), name='consumer_list'),
    path('consumer/create/', ConsumerCreateView.as_view(), name='consumer_create'),
    path('consumer/<int:pk>/', ConsumerDetailView.as_view(), name='consumer_detail'),
    path('consumer/<int:pk>/update/', ConsumerUpdateView.as_view(), name='consumer_update'),
    path('consumer/<int:pk>/delete/', ConsumerDeleteView.as_view(), name='consumer_delete'),

    path('order/list/<int:consumer_id>/', OrderListView.as_view(), name='order_list'),
    path('order/<int:consumer_id>/create/', OrderCreateView.as_view(), name='order_create'),
    path('order/<int:pk>/', OrderDetailView.as_view(), name='order_detail'),
    path('order/<int:pk>/update/', OrderUpdateView.as_view(), name='order_update'),
    path('order/<int:pk>/delete/', OrderDeleteView.as_view(), name='order_delete'),

    path('productinorder/list/<int:order_id>/', ProductInOrderListView.as_view(), name='productinorder_list'),
    path('productinorder/<int:order_id>/create/', ProductInOrderCreateView.as_view(),
         name='productinorder_create'),
    path('productinorder/<int:pk>/', ProductInOrderDetailView.as_view(), name='productinorder_detail'),
    path('productinorder/<int:pk>/update/', ProductInOrderUpdateView.as_view(),
         name='productinorder_update'),
    path('productinorder/<int:pk>/delete/', ProductInOrderDeleteView.as_view(), name='productinorder_delete'),

    path('debit/list/', DebitListView.as_view(), name='debit_list'),
    path('debit/create/', DebitCreateView.as_view(), name='debit_create'),
    path('debit/<int:pk>/', DebitDetailView.as_view(), name='debit_detail'),
    path('debit/<int:pk>/update/', DebitUpdateView.as_view(), name='debit_update'),
    path('debit/<int:pk>/delete/', DebitDeleteView.as_view(), name='debit_delete'),

    path('credit/list/', CreditListView.as_view(), name='credit_list'),
    path('credit/create/', CreditCreateView.as_view(), name='credit_create'),
    path('credit/<int:pk>/', CreditDetailView.as_view(), name='credit_detail'),
    path('credit/<int:pk>/update/', CreditUpdateView.as_view(), name='credit_update'),
    path('credit/<int:pk>/delete/', CreditDeleteView.as_view(), name='credit_delete'),

    path('balance/list/', BalanceListView.as_view(), name='balance_list'),
    path('balance/create/', BalanceCreateView.as_view(), name='balance_create'),
    path('balance/<int:pk>/', BalanceDetailView.as_view(), name='balance_detail'),
    path('balance/<int:pk>/update/', BalanceUpdateView.as_view(), name='balance_update'),
    path('balance/<int:pk>/delete/', BalanceDeleteView.as_view(), name='balance_delete'),

    path('services/transfer/<int:warehouse_id>/', warehouse.lot_to_warehouse,
         name='lot_to_warehouse'),
    path('services/transfer/<int:warehouse_id>/<int:lot_id>/', warehouse.lot_to_warehouse_detail,
            name='lot_to_warehouse_detail'),
]
