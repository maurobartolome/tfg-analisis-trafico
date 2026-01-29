#importa la librería json para manejar archivos JSON
import json
 # Voy a cargar los datos del archivo rutas.json
def cargar_rutas(rutas_archivo="../datos/rutas.json"):
    with open(rutas_archivo) as f:
    #lee el archivo f y lo convierte en un diccionario de Python
        rutas = json.load(f)
    return rutas

#Neceisito una función para cargar el mapa con sus nodos y links que serian las intersecciones y las calles, para poder saber en qué calle está cada coche
def cargar_mapa(mapa_archivo="../datos/mapa.json"):
    with open (mapa_archivo) as f:
    #lee el archivo f, que sería el mapa.json y lo convierte en un diccionario de Python para poder trabajar con él 
        mapa = json.load(f)
    return mapa

#El objetivo de cargar rutas.json es saber donde está cada coche, por ejemplo el coche 1 está en x calle durante los segundo 0 y 10
#El objetivo de cargar mapa.json es saber donde está cada calle, por ejemplo la calle A va desde x hasta y
#Con todo esto podemos saber que con el coche 1 está en una posicion durante el segundo 5 y con las localizacion de la calle podemos saber donde está exactamente el coche en ese segundo