from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from backend.utils.procesos import obtener_prioridad_procesos, clasificar_prioridad

# Create your views here.
def inicio():
    return HttpResponse("<h1>¡Hola, mundo!</h1>")

def procesos_vista(request):
    procesos = obtener_prioridad_procesos()
    for proceso in procesos:
        proceso['prioridad'] = clasificar_prioridad(proceso['nice'])
    return render(request, 'paginas/tabla.html', {'procesos': procesos})