# coding=utf-8

from django.urls import path

from . import views, lan_views

app_name = 'stressApp'
urlpatterns = [
    path('cpu_stress', views.stress_check, name='cpu_stress_check'),
    path('mem_stress', views.run_mem_check, name='run_mem_check'),
    path('hdd_stress', views.run_hdd_check, name='run_hdd_check'),
    path('stop_stress', views.stop_stress, name='stop_stress'),
    path('lan_stress', lan_views.run_item, name='run_item'),
    path('get_lan_log', lan_views.get_lan_log, name='get_lan_log'),
]

