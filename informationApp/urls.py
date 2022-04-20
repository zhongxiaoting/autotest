# coding=utf-8

from django.urls import path

from . import views

app_name = 'informationApp'
urlpatterns = [
    path('cpu_mce', views.cpu_mce_check, name='cpu_mce_check'),
    path('mem_ecc', views.mem_ecc_check, name='mem_ecc_check'),
    path('cpu_info', views.cpu_info, name='cpu_info_check'),
    path('memory_info', views.memory_info, name='memory_info'),
    path('hdd_info', views.hdd_info_check, name='hdd_info'),
    path('network_info', views.network_info_check, name='network_info'),
    path('system_info', views.system_info, name='system_info')
]
