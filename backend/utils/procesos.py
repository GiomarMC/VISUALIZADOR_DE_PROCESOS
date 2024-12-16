import psutil
import random
import time

def obtener_prioridad_procesos():
    procesos = []
    tiempo_actual = 0
    for proceso in psutil.process_iter(attrs=['pid', 'name', 'nice', 'status', 'cpu_percent', 'memory_info']):
        try:
            info = proceso.info
            tiempo_actual = tiempo_actual + random.randint(1, 4)
            info['arrival_time'] = tiempo_actual
            info['time_execution'] = random.randint(1, 10)
            procesos.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procesos