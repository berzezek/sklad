from django.shortcuts import render, redirect

from ..models import ProductInLot, Lot, LotCost, Warehouse, ProductInWarehouse, ProductInOrder


def product_cost_price(lot_id=None, product_in_lot_id=None):
    lot = Lot.objects.get(id=lot_id)
    product_in_lot = ProductInLot.objects.get(id=product_in_lot_id)
    products_in_lot_total_quantity = lot.get_products_quantity()
    product_in_lot_total_weight = lot.get_products_weight()
    lots_costs = LotCost.objects.filter(lot=lot_id)
    cost_price = 0
    for lot_cost in lots_costs:
        if lot_cost.distribution == 'equal':
            cost_price += lot_cost.amount_spent / products_in_lot_total_quantity
        elif lot_cost.distribution == 'by_weight':
            cost_price += lot_cost.amount_spent / product_in_lot_total_weight * product_in_lot.product.weight
        elif lot_cost.distribution == 'by_price':
            cost_price += lot_cost.amount_spent * product_in_lot.purchase_price / lot.get_total_lot_purchase_price()

    product_in_lot_cost_price = product_in_lot.purchase_price + cost_price

    return product_in_lot_cost_price


def get_wholesale_price(product_in_lot=None, warehouse_id=None):
    product_in_warehouse = ProductInWarehouse.objects.filter(
        product=product_in_lot.product,
        warehouse=warehouse_id
    ).last()
    return product_in_warehouse.wholesale_price


def get_retail_price(product_in_lot=None, warehouse_id=None):
    product_in_warehouse = ProductInWarehouse.objects.filter(
        product=product_in_lot.product,
        warehouse=warehouse_id
    ).last()
    return product_in_warehouse.retail_price


def lot_to_warehouse(request, warehouse_id=None, lot_id=None):
    lot_list_delivered = Lot.objects.filter(status='delivered')
    warehouse = Warehouse.objects.get(pk=warehouse_id)
    return render(request, 'warehouse/services/transfer_to_warehouse/to_warehouse.html', {
        'lot_list_delivered': lot_list_delivered,
        'warehouse': warehouse,
    })


def get_product_for_transfer(products_in_lot, warehouse_id, lot_id):
    products_for_transfer = [ ]
    for pil in products_in_lot:
        pft = {
            'pk': pil.pk,
            'product': pil.product,
            'warehouse': warehouse_id,
            'description': pil.description,
            'price': pil.purchase_price,
            'cost_price': product_cost_price(lot_id, pil.pk),
            'quantity': pil.quantity,
            'total_weight': pil.get_total_weight,
        }
        products_for_transfer.append(pft)
    return products_for_transfer


def lot_to_warehouse_detail(request, warehouse_id=None, lot_id=None):
    lot = Lot.objects.get(pk=lot_id)
    if lot.status != 'delivered':
        return redirect('warehouse:warehouse_list')
    warehouse = Warehouse.objects.get(pk=warehouse_id)
    products_in_lot_pre_transfer = ProductInLot.objects.filter(lot=lot_id)
    products_in_lot = get_product_for_transfer(products_in_lot_pre_transfer, warehouse_id, lot_id)
    if request.method == 'GET':
        return render(request, 'warehouse/services/transfer_to_warehouse/to_warehouse_detail.html', {
            'lot': lot,
            'products_in_lot': products_in_lot,
            'warehouse': warehouse,
        })
    elif request.method == 'POST':
        for pil in products_in_lot:
            ProductInWarehouse.objects.create(
                product=pil[ 'product' ],
                warehouse=warehouse,
                quantity=pil[ 'quantity' ],
                cost_price=pil[ 'cost_price' ],
                transaction='in',
            )
        lot.status = 'in_warehouse'
        lot.save()
        return redirect('warehouse:warehouse_list')


def warehouse_to_order(warehouse_id=None, order_id=None):
    warehouse = Warehouse.objects.get(pk=warehouse_id)
    products_in_order = ProductInOrder.objects.filter(order=order_id)
    for pio in products_in_order:
        ProductInWarehouse.objects.create(
            product=pio.product,
            warehouse=warehouse,
            quantity=pio.quantity,
            cost_price=None,
            transaction='out',
        )
