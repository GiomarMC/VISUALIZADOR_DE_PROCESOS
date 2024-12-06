from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('tabla', views.procesos_vista, name='tabla_procesos'),
]