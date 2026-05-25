import json
import zipfile
from io import StringIO

def cargar_rutas(rutas_archivo="../datos/rutas.json", zip_file=None):
    """Carga el archivo de rutas y lo convierte en un diccionario de Python
       El objetivo de cargar rutas.json es saber donde está cada coche, por ejemplo el coche 1 está en x calle durante los segundo 0 y 10
    
    :param rutas_archivo: Ruta del archivo rutas.json (o ruta dentro del ZIP)
    :param zip_file: Objeto zipfile.ZipFile abierto (si es None, carga del sistema de archivos)
    :return: Diccionario con las rutas de los coches
    """
    if zip_file is not None:
        # Cargar desde ZIP
        with zip_file.open(rutas_archivo) as f:
            rutas = json.load(f)
    else:
        # Cargar del sistema de archivos
        with open(rutas_archivo) as f:
            rutas = json.load(f)
    return rutas

def cargar_mapa(mapa_archivo="../datos/mapa.json", zip_file=None):
    """Carga el archivo de mapa y lo convierte en un diccionario de Python
        El objetivo de cargar mapa.json es saber donde está cada calle, por ejemplo la calle A va desde x hasta y

    :param mapa_archivo: Ruta del archivo mapa.json (o ruta dentro del ZIP)
    :param zip_file: Objeto zipfile.ZipFile abierto (si es None, carga del sistema de archivos)
    :return: Diccionario con el mapa (nodos y links)
    """
    if zip_file is not None:
        # Cargar desde ZIP
        with zip_file.open(mapa_archivo) as f:
            mapa = json.load(f)
    else:
        # Cargar del sistema de archivos
        with open(mapa_archivo) as f:
            mapa = json.load(f)
    return mapa




