# coding=utf-8

from django.urls import path

from . import views

app_name = 'informationApp'
urlpatterns = [
    path('cpu_mce/', views.cpu_mce_check, name='cpu_mce_check'),
    path('mem_ecc/', views.mem_ecc_check, name='mem_ecc_check'),
]
