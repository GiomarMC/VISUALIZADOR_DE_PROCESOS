import psutil

def obtener_prioridad_procesos():
    procesos = []
    for proceso in psutil.process_iter(attrs=['pid', 'name', 'nice', 'status', 'cpu_percent', 'memory_info']):
        try:
            procesos.append(proceso.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procesos

def clasificar_prioridad(nice):
    if nice < 0:
        return "Alta"
    elif nice == 0:
        return "Normal"
    else:
        return "Baja"