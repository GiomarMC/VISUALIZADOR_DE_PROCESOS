from django.urls import path
from . import views

urlpatterns = [
    path('', views.procesos_vista, name='tabla_procesos'),
    path('visualizacion/', views.visualizacion, name='visualizacion'),
    path('datos_procesos/', views.obtener_datos_procesos, name='datos_procesos'),
]