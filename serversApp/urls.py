from django.urls import path

from . import views

app_name = 'serversApp'
urlpatterns = [
    path('', views.create_server, name='server'),
]
