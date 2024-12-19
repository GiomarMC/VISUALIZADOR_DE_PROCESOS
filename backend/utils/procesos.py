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

def verificar_cola_vacia(id_nucleo, cola, nombre_algoritmo):
    if cola.empty():
        print(f"[{nombre_algoritmo}] Núcleo {id_nucleo}: Cola vacía, todos los procesos completados.")

def round_robin(id_nucleo, cola, lock, evento_terminado, quantum=4):
    while not evento_terminado.is_set():
        with lock:
            if cola.empty():
                verificar_cola_vacia(id_nucleo, cola, "Round Robin")
                continue

            proceso = cola.get()
            print(f"[Round Robin] Núcleo {id_nucleo}: Proceso {proceso['pid']} entrando a ejecución. Tiempo restante: {proceso['time_execution']}")

            tiempo_restante = proceso['time_execution'] - quantum
            time.sleep(1)

            if tiempo_restante > 0:
                proceso['time_execution'] = tiempo_restante
                print(f"[Round Robin] Núcleo {id_nucleo}: Proceso {proceso['pid']} pausado. Tiempo restante: {tiempo_restante}")
                cola.put(proceso)
            else:
                print(f"[Round Robin] Núcleo {id_nucleo}: Proceso {proceso['pid']} completado")


def shortest_job_first(id_nucleo, cola, lock, evento_terminado):
    while not evento_terminado.is_set():
        with lock:
            if cola.empty():
                verificar_cola_vacia(id_nucleo, cola, "SJF")
                continue

            proceso = min(list(cola.queue), key=lambda x: x['time_execution'])
            cola.queue.remove(proceso)

            print(f"[SJF] Núcleo {id_nucleo}: Proceso {proceso['pid']} entrando a ejecución. Tiempo: {proceso['time_execution']}")

            time.sleep(1)
            print(f"[SJF] Núcleo {id_nucleo}: Proceso {proceso['pid']} completado")


def first_come_first_served(id_nucleo, cola, lock, evento_terminado):
    while not evento_terminado.is_set():
        with lock:
            if cola.empty():
                verificar_cola_vacia(id_nucleo, cola, "FCFS")
                continue

            proceso = cola.get()
            print(f"[FCFS] Núcleo {id_nucleo}: Proceso {proceso['pid']} entrando a ejecución. Tiempo: {proceso['time_execution']}")

            time.sleep(1)
            print(f"[FCFS] Núcleo {id_nucleo}: Proceso {proceso['pid']} completado")


def prioridad(id_nucleo, cola, lock, evento_terminado):
    while not evento_terminado.is_set():
        with lock:
            if cola.empty():
                verificar_cola_vacia(id_nucleo, cola, "Prioridad")
                continue

            proceso = min(list(cola.queue), key=lambda x: x['nice'])
            cola.queue.remove(proceso)

            print(f"[Prioridad] Núcleo {id_nucleo}: Proceso {proceso['pid']} entrando a ejecución con prioridad {proceso['nice']} y tiempo {proceso['time_execution']}")

            time.sleep(1)
            print(f"[Prioridad] Núcleo {id_nucleo}: Proceso {proceso['pid']} completado")

def balanceador_de_carga(colas, lock, evento_terminado):
    while not evento_terminado.is_set():
        with lock:
            tamanio = [cola.qsize() for cola in colas]
            max_index = tamanio.index(max(tamanio))
            min_index = tamanio.index(min(tamanio))

            if (tamanio[max_index] - tamanio[min_index] > 1):
                proceso_transferido = colas[max_index].get()
                colas[min_index].put(proceso_transferido)
                print(f"[Balanceador de Carga] Proceso {proceso_transferido['pid']} de núcleo {max_index + 1} a núcleo {min_index + 1}")
        time.sleep(1)

def verificar_colas_final(colas):
    todas_vacias = True
    for i, cola in enumerate(colas, start=1):
        if cola.empty():
            print(f"[FINAL] Núcleo {i}: Cola vacía, todos los procesos completados.")
        else:
            todas_vacias = False
            print(f"[FINAL] Núcleo {i}: Procesos pendientes: {list(cola.queue)}")
    return todas_vacias

def iniciar_simulacion(procesos):
    procesos_globales = procesos
    colas = [Queue() for _ in range(4)]
    lock = threading.Lock()
    evento_terminado = threading.Event()

    for cola in colas:
        asignar_procesos_iniciales(procesos_globales, cola, 10, lock)

    hilos_nucleos = [
        threading.Thread(target=round_robin, args=(1, colas[0], lock, evento_terminado)),
        threading.Thread(target=shortest_job_first, args=(2, colas[1], lock, evento_terminado)),
        threading.Thread(target=first_come_first_served, args=(3, colas[2], lock, evento_terminado)),
        threading.Thread(target=prioridad, args=(4, colas[3], lock, evento_terminado)),
    ]

    hilos_agregadores = [
        threading.Thread(target=agregar_procesos_a_cola, args=(procesos_globales, colas[i], lock, i + 1, evento_terminado)) for i in range(4)
    ]

    hilo_balanceador = threading.Thread(target=balanceador_de_carga, args=(colas, lock, evento_terminado))

    try:
        for hilo in hilos_nucleos + hilos_agregadores:
            hilo.start()

        hilo_balanceador.start()

        time.sleep(540)
        evento_terminado.set()

        for hilo in hilos_nucleos + hilos_agregadores:
            hilo.join()

        hilo_balanceador.join()

        if verificar_colas_final(colas):
            print("Simulación completada correctamente, todos los procesos han sido ejecutados.")
        else:
            print("Algunos procesos no fueron ejecutados correctamente.")

    except RuntimeError as e:
        print(f"Error en la simulación: {e}")