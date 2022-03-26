# coding=utf-8

from django.urls import path

from . import views

app_name = 'stressApp'
urlpatterns = [
    path('cpu_stress/', views.stress_check, name='cpu_stress_check'),
    path('mem_stress/', views.run_mem_check, name='run_mem_check'),
    path('hdd_stress/', views.run_hdd_check, name='run_hdd_check'),
    path('get_hdd_log/', views.get_hdd_log, name='get_hdd_log'),


]