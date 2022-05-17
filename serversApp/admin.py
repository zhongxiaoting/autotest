from django.contrib import admin

# Register your models here.

from .models import Servers, SubmitLog


# admin.site.register(Servers)
# admin.site.register(SubmitLog)


@admin.register(Servers)
class ServersAdmin(admin.ModelAdmin):
    list_display = ['sn', 'worker']
    search_fields = ['sn', 'worker__username']


@admin.register(SubmitLog)
class SubmitLogAdmin(admin.ModelAdmin):
    list_display = ['server', 'server_worker', 'server_name', 'download']
    search_fields = ['server__sn', 'server__worker']