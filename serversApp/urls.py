# coding=utf-8

from django.urls import path

from . import views

app_name = 'serversApp'
urlpatterns = [
    path('input', views.create_server, name='server'),
    path('upload', views.upload, name='upload'),
    # path('download', views.download, name='download')
]
