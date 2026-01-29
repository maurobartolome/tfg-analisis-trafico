 #El objetivo de esta funcion es un diccionario y contar cuantos coches hay en cada calle en un instante de tiempo dado
def contar_coches_instantes(rutas, tiempo):
    coches_por_calle = {}
    
    #para cada coche tengo que hacer:
    #rutas.items produce un diccionario con clave el id del coche y el valor los datos de ese coche
    for car_id, car in rutas.items():
        if not car_id.isdigit(): # me aseguro que solo itero sobre los coches y no sobre otras claves como runtime
            continue
        times = car["times"]  # obtengo los tiempos asociados al coche actual

# dentro del array times que tiene esta forma car["times"] = [[0, 10],->id=0 [10, 25],->id=1 
#enumerate produce pares, en este caso el id del intervalo y el propio intervalo
#tiempoini y tiempo fin son los valores del intervalo
        for id, (tiempoini, tiempofin) in enumerate(times): 
            if tiempoini <= tiempo < tiempofin:  # si el tiempo dado está dentro del intervalo del coche
                path = car["path"]  #Obtenemos la lista de todas las calles por las que pasa el coche que seria como   "path": [[[45.08, 7.65], [45.09, 7.66]],  # id=0: calle en este intervalo[[45.09, 7.66], [45.10, 7.67]],  # id=1: calle en este intervalo
                
                # Pongo una tupla porque una lista no puede ser claves de diccionario. Las tuplas si pueden porque son inmutables entonces las claves necesitan ser estables.
                calle_actual = tuple(map(tuple, path[id])) 
                if calle_actual not in coches_por_calle:
                    coches_por_calle[calle_actual] = 0  # inicializo el contador si es la primera vez que veo esta calle
                coches_por_calle[calle_actual] += 1  # incremento el contador de coches en esa calle
                break  # una vez encontrado el intervalo, no necesito seguir buscando para este coche
    return coches_por_calle

#Esta funcion tiene como entrada los coches y TODOS los tiempos, entonces para cada instante se llama a la funcion coches_instantes y nos dice que hay en todos los segundos
def contar_coches_todos_tiempos(rutas, time_grid):
    contar_tiempos ={} # diccionario donde se guardará el resultado
    for tiempo in time_grid: # Itera sobre cada tiempo en la cuadrícula de tiempo
        contar_tiempos[tiempo] = contar_coches_instantes(rutas, tiempo) # Llama a la función para contar coches en el tiempo actual y almacena el resultado
    return contar_tiempos