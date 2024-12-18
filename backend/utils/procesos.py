import psutil
import random
import time
import threading
from queue import Queue

def obtener_procesos():
    procesos = []
    tiempo_actual = 0
    for proceso in psutil.process_iter(attrs=['pid', 'name', 'nice', 'status', 'cpu_percent', 'memory_info']):
        try:
            info = proceso.info
            tiempo_actual = tiempo_actual + random.randint(1, 4)
            info['arrival_time'] = tiempo_actual
            info['time_execution'] = random.randint(5, 10)
            procesos.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return procesos

def asignar_procesos_iniciales(procesos_globales, cola, cantidad_inicial, lock):
    with lock:
        for _ in range(cantidad_inicial):
            if procesos_globales:
                proceso = procesos_globales.pop(0)
                cola.put(proceso)
                print(f"Proceso inicial asignado: {proceso['pid']}")

def agregar_procesos_a_cola(procesos_globales, cola, lock, id_nucleo, evento_terminado):
    while not evento_terminado.is_set():
        with lock:
            if procesos_globales:
                proceso = procesos_globales.pop(0)
                cola.put(proceso)
                print(f"Proceso {proceso['pid']} asignado a nucleo {id_nucleo}")
        time.sleep(random.randint(1, 10))   

def round_robin(id_nucleo, cola, lock, evento_terminado, quantum=4):
    while not evento_terminado.is_set():
        with lock:
            if cola.empty():
                continue
            proceso = cola.get()
            tiempo_restante = proceso['time_execution'] - quantum
            if tiempo_restante > 0:
                proceso['time_execution'] = tiempo_restante
                print(f"Nucleo {id_nucleo} ejecutando proceso {proceso['pid']} con tiempo restante {tiempo_restante}")
                cola.put(proceso)
            else:
                print(f"Nucleo {id_nucleo} completo proceso {proceso['pid']}")
            time.sleep(1)

def shortest_job_first(id_nucleo, cola, lock, evento_terminado):
    while not evento_terminado.is_set():
        with lock:
            if cola.empty():
                continue
            procesos_ordenados = sorted(list(cola.queue), key=lambda x: x['time_execution'])
            cola.queue.clear()
            for proceso in procesos_ordenados:
                cola.put(proceso)
            proceso = cola.get()
            print(f"Nucleo {id_nucleo} ejecutando proceso {proceso['pid']} con tiempo de ejecucion {proceso['time_execution']}")
        time.sleep(1)

def first_come_first_served(id_nucleo, cola, lock, evento_terminado):
    while not evento_terminado.is_set():
        with lock:
            if cola.empty():
                continue
            proceso = cola.get()
            print(f"Nucleo {id_nucleo} ejecutando proceso {proceso['pid']} con tiempo de ejecucion {proceso['time_execution']}")
        time.sleep(1)

def prioridad(id_nucleo, cola, lock, evento_terminado):
    while not evento_terminado.is_set():
        with lock:
            if cola.empty():
                continue
            procesos_ordenados = sorted(list(cola.queue), key=lambda x: x['nice'], reverse=True)
            cola.queue.clear()
            for proceso in procesos_ordenados:
                cola.put(proceso)
            proceso = cola.get()
            print(f"Nucleo {id_nucleo} ejecutando proceso {proceso['pid']} con prioridad {proceso['nice']}")
        time.sleep(1)

def balanceador_de_carga(colas, lock, evento_terminado):
    while not evento_terminado.is_set():
        with lock:
            tamanio = [cola.qsize() for cola in colas]
            max_index = tamanio.index(max(tamanio))
            min_index = tamanio.index(min(tamanio))

            if(tamanio[max_index] - tamanio[min_index] > 1):
                proceso_transferido = colas[max_index].get()
                colas[min_index].put(proceso_transferido)
                print(f"Proceso {proceso_transferido['pid']} de nucleo {max_index + 1} a nucleo {min_index + 1}")
        time.sleep(1)

def iniciar_simulacion():
    procesos_globales = obtener_procesos()
    colas = [Queue() for _ in range(4)]
    lock = threading.Lock()
    evento_terminado = threading.Event()

    asignar_procesos_iniciales(procesos_globales, colas, 10, lock)

    hilos_nucleos = [
        threading.Thread(target=round_robin, args=(1, colas[0], lock, evento_terminado)),
        threading.Thread(target=shortest_job_first, args=(2, colas[1], lock, evento_terminado)),
        threading.Thread(target=first_come_first_served, args=(3, colas[2], lock, evento_terminado)),
        threading.Thread(target=prioridad, args=(4, colas[3], lock, evento_terminado)),
    ]

    hilos_agregadores = [
        threading.Thread(target=agregar_procesos_a_cola, args=(procesos_globales, colas[i], lock, i + 1, evento_terminado)) for i in range(4)
    ]

    hilo_balanceador = threading.Thread(target=balanceador_de_carga, args=(colas,lock, evento_terminado))

    try:
        for hilo in hilos_nucleos + hilos_agregadores:
            hilo.start()

        hilo_balanceador.start()
        time.sleep(20)
        evento_terminado.set()

        for hilo in hilos_nucleos + hilos_agregadores:
            hilo.join()

        hilo_balanceador.join()

    except RuntimeError as e:
        print(f"Error en la simulacion: {e}")