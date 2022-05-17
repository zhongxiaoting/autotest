from django.contrib import admin
from .models import Mes_server, Fireware, Cpu
# Register your models here.


@admin.register(Mes_server)
class Mes_serverAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'input_date', 'output_date']
    search_fields = ['product_name', 'input_date', 'output_date']


@admin.register(Fireware)
class FirewareAdmin(admin.ModelAdmin):
    list_display = ['product', 'sn', 'bois_version', 'bmc_version']
    search_fields = ['product__product_name', 'sn']


@admin.register(Cpu)
class FirewareAdmin(admin.ModelAdmin):
    list_display = ['product', 'sn', 'type']
    search_fields = ['product__product_name', 'sn', 'type']
