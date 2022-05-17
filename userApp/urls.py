# coding=utf-8

from django.urls import path

from . import views

app_name = 'userApp'
urlpatterns = [
    path('login', views.user_login, name='login'),
    path('logout', views.user_logout, name='logout'),

]
