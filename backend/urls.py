from django.urls import path
from . import views

urlpatterns = [
    path('', views.procesos_vista, name='tabla_procesos'),
]