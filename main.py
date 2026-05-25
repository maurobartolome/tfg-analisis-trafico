import json
from cargar_datos import cargar_rutas, cargar_mapa
from contar_datos import contar_coches_todos_tiempos, rb_usage 


#Voy a cargar tanto las rutas como el mapa
rutas = cargar_rutas()
mapa = cargar_mapa()

N_RB = 222
n_max_global = max(road['max_toded'] for road in mapa['links'])
rbs_por_coche = N_RB // n_max_global

#Aquío calculo el tiempo maximo de la simulacion para definir el eje de tiempo, lo hago igual que en tiempomaximo.py
T_max = max(car["times"][-1][1] for car_id, car in rutas.items() if car_id.isdigit()) 

#Aquí imprimo el tiempo máximo de simulación, apartir de ese T_max deberían ser 0 los coches en cualquier calle
print(f"Tiempo máximo de simulación: {T_max} segundos")


#Convierte los numeros decimales de T_max a enteros para definir el eje de tiempos
#Crea los numeros 0,1,2,etc
# Creo una lista con los tiempos desde 0 hasta T_max
time_grid = list(range(0, int(T_max) + 2))


#Aquí cuento los coches en todas las calles para todos los tiempos, time_grid es exportado de tiempomaxio.py
resultados = contar_coches_todos_tiempos(rutas,time_grid)
# Mostrar coches por segundo (SIMPLE)
print("Coches por segundo")


#Esto es para mostrar los coches que hay en movimiento 
#Obtiene las claves de resultados, que son los tiempos  y las ordena de menor a mayor
#Itera sobre cada tiempo ordenado
for tiempo in sorted(resultados.keys()):
    #Accede al diccionario de ese tiempo que se está iterando
    #Guarda en total_coches la suma de todos los valores del diccionario, que son los coches en cada calle
    total_coches = sum(resultados[tiempo].values())
    print(f"Segundo {int(tiempo)}: {total_coches} coches en movimiento")

    
    #Ahora en cada tiempo del primer bucle for, itero en cada calle y cuento cuantos coches hay en esa calle en ese momento, si no hay coches en esa calle no aparece 
    #En 
    for calle, num_coches in resultados[tiempo].items():
        inicio = calle[0]
        fin = calle[1]
        print(f"  Calle {inicio} → {fin}: {num_coches} coches")
        
# Versión fija
from riv_config_fijo import calcular_riv_simulacion
riv_simulacion = calcular_riv_simulacion(resultados, N_BWP=N_RB, rbs_por_coche=24)

# Versión variable
from riv_config_variable import calcular_riv_simulacion
riv_simulacion = calcular_riv_simulacion(resultados, N_BWP=222)
