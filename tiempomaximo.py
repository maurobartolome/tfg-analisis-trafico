import json

# Abrir el archivo rutas.json y cargar el contenido
with open("../datos/rutas.json") as f:
    rutas = json.load(f) #ahora rutas es un diccionario
# Ahora voy a crear la variable para guardar el tiempo máximo y asi poner limite superior al eje de tiempo 
T_max = max (  
    car["times"][-1][1]  # Lo que hace el [-1][1] es acceder al utlimo intervalo de tiempo del coche y coger el tiempo donde finaliza ese intervalo, y por tanto su tiempo final
    for car_id, car in rutas.items() # rutas.items() lo que hace es devolver pares (car_id, car), devolviendo como clave el id del coche y como valor los datos asociados a cada coche como path, times y runtime
    if car_id.isdigit() # esto lo utilizo para asegurarme que el car_id que estoy iterando en el for es un numero y no un runtime o cualquier otra cosa
)
print (f"Tiempo máximo de simulación: {T_max} segundos")

#Convierte los numeros decimales de T_max a enteros para definir el eje de tiempos
#Crea los numeros 0,1,2,etc
 # Creo una lista con los tiempos desde 0 hasta T_max
time_grid = list(range(0, int(T_max) + 2))  