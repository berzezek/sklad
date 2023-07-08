from django.apps import AppConfig
from django.db.models.signals import post_save


class WarehouseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warehouse'

    def ready(self):
        import warehouse.signals
        post_save.connect(warehouse.signals.create_cost_in_and_out_product_in_warehouse, sender='warehouse.Order')
        post_save.connect(warehouse.signals.create_cost_out_for_buy_lot, sender='warehouse.Lot')