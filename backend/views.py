from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from backend.utils.procesos import obtener_procesos
# Create your views here.
def procesos_vista(request):
    procesos = obtener_procesos()
    return render(request, 'paginas/tabla.html', {'procesos': procesos})