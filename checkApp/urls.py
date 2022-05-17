# coding=utf-8

from django.urls import path

from . import views

app_name = 'checkApp'
urlpatterns = [
    path('system_checkout', views.system_checkout, name='system_checkout'),
    path('cpu_checkout', views.cpu_checkout, name='cpu_checkout'),

]