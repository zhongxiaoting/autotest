# coding=utf-8

from django.urls import path

from . import views

app_name = 'stressApp'
urlpatterns = [
    path('cpu_stress/', views.stress_check, name='cpu_stress_check'),
    # path('test_websocket', views.test_websocket , name='test_websocket'),
]