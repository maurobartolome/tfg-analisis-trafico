import json

def cargar_rutas(rutas_archivo="../datos/rutas.json"):
    """Carga el archivo de rutas y lo convierte en un diccionario de Python
       El objetivo de cargar rutas.json es saber donde está cada coche, por ejemplo el coche 1 está en x calle durante los segundo 0 y 10
    
    :param rutas_archivo: Ruta del archivo rutas.json
    :return: Diccionario con las rutas de los coches
    """
    with open(rutas_archivo) as f:
        rutas = json.load(f)
    return rutas

def cargar_mapa(mapa_archivo="../datos/mapa.json"):
    """Carga el archivo de mapa y lo convierte en un diccionario de Python
        El objetivo de cargar mapa.json es saber donde está cada calle, por ejemplo la calle A va desde x hasta y

    :param mapa_archivo: Ruta del archivo mapa.json
    :return: Diccionario con el mapa (nodos y links)
    """
    with open (mapa_archivo) as f:
        mapa = json.load(f)
    return mapa


