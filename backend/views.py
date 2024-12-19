from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from backend.utils.procesos import obtener_procesos
from threading import Thread
# Create your views here.

procesos = obtener_procesos()

def procesos_vista(request):
    global procesos
    return render(request, 'paginas/tabla.html', {'procesos': procesos})

def visualizacion(request):
    return render(request, 'paginas/visualizacion.html')

def obtener_datos_procesos(request):
    global procesos
    return JsonResponse({'procesos': procesos}, safe=False)