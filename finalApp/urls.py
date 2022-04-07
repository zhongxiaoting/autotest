# coding=utf-8

from django.urls import path

from . import views

app_name = 'finalApp'
urlpatterns = [
    path('run_black/', views.run_item, name='run_item'),
    path('get_black_log/', views.get_black_log, name='get_black_log'),
]