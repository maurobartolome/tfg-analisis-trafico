
def contar_coches_instantes(rutas, tiempo):
    """El objetivo de esta funcion es un diccionario y contar cuantos coches hay en cada calle en un instante de tiempo dado
    para cada coche tengo que hacer:
        rutas.items produce un diccionario con clave el id del coche y el valor los datos de ese coche
        me aseguro que solo itero sobre los coches y no sobre otras claves como runtime
        obtengo los tiempos asociados al coche actual
    
    dentro del array times que tiene esta forma car["times"] = [[0, 10],->id=0 [10, 25],->id=1 
        enumerate produce pares, en este caso el id del intervalo y el propio intervalo
        tiempoini y tiempo fin son los valores del intervalo
        si el tiempo dado está dentro del intervalo del coche
        Obtenemos la lista de todas las calles por las que pasa el coche que seria como   "path": [[[45.08, 7.65], [45.09, 7.66]],  # id=0: calle en este intervalo[[45.09, 7.66], [45.10, 7.67]],  # id=1: calle en este intervalo
    
    Pongo una tupla porque una lista no puede ser claves de diccionario. Las tuplas si pueden porque son inmutables entonces las claves necesitan ser estables.

    
    :param rutas: Diccionario con los datos de los coches (rutas.json)
    :param tiempo: Instante de tiempo para el que se quiere contar
    :return: Diccionario {calle_tuple: num_coches}
    """
    coches_por_calle = {}
    

    for car_id, car in rutas.items():
        if not car_id.isdigit(): 
            continue
        times = car["times"]  
        
        for id, (tiempoini, tiempofin) in enumerate(times): 
            if tiempoini <= tiempo < tiempofin:  
                path = car["path"]  

                calle_actual = tuple(map(tuple, path[id])) 
                if calle_actual not in coches_por_calle:
                    coches_por_calle[calle_actual] = 0  
                coches_por_calle[calle_actual] += 1  
                break  
    return coches_por_calle

def contar_coches_todos_tiempos(rutas, time_grid):
    """Cuenta cuántos coches hay en cada calle para todos los tiempos dados.
       Esta funcion tiene como entrada los coches y TODOS los tiempos, entonces para cada instante se llama a la funcion coches_instantes y nos dice que hay en todos los segundos
    Itera sobre cada tiempo en la cuadrícula de tiempo
    Llama a la función para contar coches en el tiempo actual y almacena el resultado

    :param rutas: Diccionario con los datos de los coches (rutas.json)
    :param time_grid: Lista de instantes de tiempo
    :return: Diccionario {tiempo: {calle_tuple: num_coches}}
    """
    contar_tiempos ={} 
    for tiempo in time_grid: 
        contar_tiempos[tiempo] = contar_coches_instantes(rutas, tiempo)  
    return contar_tiempos



def contar_vehiculos_unicos_por_calle(rutas):
    """Cuenta cuántos vehículos únicos han pasado por cada calle.
    para cada coche tengo que hacer:
    rutas.items produce un diccionario con clave el id del coche y el valor los datos de ese coche
        obtengo los tiempos asociados al coche actual
        obtengo la lista de todas las calles por las que pasa el coche
        Asegura que no se exceda el índice máximo entre times y path, elijo el minimo para evitar errores y asi no desincronizasr ambos arrays
        Esto recorre desde el id 0 hasta el mínimo entre la longitud de times o de path
            Tengo que hacer map porque path tiene la siguiente forma [[x1, y1], [x2, y2]] para pasarlo a ((x1, y1), (x2, y2))
            Tiene que tener esta forma porque los diccionarios necesitan claves inmutables y las listas no lo son
            Añado el coche a la calle que estoy recorriendo en el bucle for en cada id, si la calle no existe en el diccionario la inicializo con un conjunto vacio
            Añado el id del coche al conjunto de coches que han pasado por esa calle
            
    :param rutas: Diccionario con los datos de los coches (rutas.json)
    :return: Devuelve un Diccionario {calle_tuple: num_vehiculos_unicos} con key la calle, y como value el numero de coches unicos que pasan por ella.Recorre cada coche y cuenta cuántos vehículos distintos han pasado por cada carretera durante toda la simulación.
    """
    vehiculos_por_calle = {}
    

    for car_id, car in rutas.items():
        if not car_id.isdigit():
            continue
        times = car["times"] 
        path = car["path"] 
        indice = min(len(times), len(path))  
        for id in range(indice): 
             calle = tuple(map(tuple, path[id]))  
             if calle not in vehiculos_por_calle:
                vehiculos_por_calle[calle] = set()
             vehiculos_por_calle[calle].add(car_id) 
    return {calle: len(coches) for calle, coches in vehiculos_por_calle.items()} 




def rb_usage(mapa, contar_tiempos):
    """Calcula el porcentaje de uso de RBs en cada carretera y tiempo.
       Recorre cada carretera del mapa
       Convierte el origen y destino a tupla para usarlo como clave, creando la clave de la calle como (origen, destino)
       Almacena el número máximo de RBs para esa calle en un diccionario    
    Recorre cada instante de tiempo y las calles con coches en ese instante
        Recorre cada calle y el número de coches en ese instante, comprobando si esa calle existe en el mapa
        Obtiene la capacidad máxima de RBs para esa calle
        Calcula el porcentaje de uso de RBs como el número de coches dividido por la capacidad máxima
        
    
    :param mapa: Diccionario del mapa (mapa.json con 'links' y 'max_toded')
    :param contar_tiempos: Diccionario {tiempo: {calle_tuple: num_coches}}
    :return: Diccionario {calle_tuple: {tiempo: porcentaje}}
    """
    rb_por_calle ={}
    for road in mapa['links']:
        start = tuple(road['source'])
        end = tuple(road['target'])
        calle = (start, end)
        rb_por_calle[calle] = road['max_toded']
    uso_rb = {}
    for tiempo, calles in contar_tiempos.items():
        for calle, num_coches in calles.items():
            if calle in rb_por_calle:
                rb_max = rb_por_calle[calle]
                porcentaje = num_coches / rb_max if rb_max > 0 else 0
                
                if calle not in uso_rb:
                    uso_rb[calle] = {}
                uso_rb[calle][tiempo] = porcentaje
    return uso_rb
