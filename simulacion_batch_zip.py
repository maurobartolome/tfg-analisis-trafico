import math
import json
import zipfile
import csv
from pathlib import Path
from cargar_datos import cargar_rutas, cargar_mapa
from contar_datos import contar_coches_todos_tiempos
from simulacion_ahorro import (
    CONFIGURACIONES, MU, SCS_HZ, T_SIMBOLO_S, T_SLOT_MS, PDB_MS, S, G, 
    BITRATE_BPS, SE, F_bits, generar_frame_bits, b_simbolo, b_slot, R,
    P_ACTIVA, P_ASM1, P_ASM2, P_ASM3, P_TRANS_ASM1, P_TRANS_ASM2, 
    P_TRANS_ASM3, SW_ASM1_SLOTS, SW_ASM2_SLOTS, SW_ASM3_SLOTS,
    calcular_consumo_instante, simular_configuracion
)


def calcular_percentil(datos, percentil):
    """Calcular percentil sin numpy"""
    if not datos:
        return 0
    sorted_datos = sorted(datos)
    indice = (percentil / 100) * (len(sorted_datos) - 1)
    lower = int(indice)
    upper = lower + 1
    if upper >= len(sorted_datos):
        return sorted_datos[lower]
    fraccion = indice - lower
    return sorted_datos[lower] * (1 - fraccion) + sorted_datos[upper] * fraccion

def calcular_desv_estandar(datos):
    """Calcular desviación estándar sin numpy"""
    if not datos or len(datos) < 2:
        return 0
    media = sum(datos) / len(datos)
    varianza = sum((x - media) ** 2 for x in datos) / (len(datos) - 1)
    return varianza ** 0.5

def procesar_zip(ruta_zip, carpeta_salida="../resultados"):
    """
    Procesa todos los archivos JSON dentro de un ZIP
    y calcula la MEDIA de resultados de simulacion_ahorro.
    
    :param ruta_zip: Ruta al archivo ZIP
    :param carpeta_salida: Carpeta donde guardar resultados
    """
    # Crear carpeta de salida si no existe
    Path(carpeta_salida).mkdir(parents=True, exist_ok=True)
    
    # Acumuladores para estadísticas completas (guardar todos los valores)
    acumuladores = {
        "A": {"ahorro": [], "consumo": [], "baseline": []},
        "B": {"ahorro": [], "consumo": [], "baseline": []},
        "C": {"ahorro": [], "consumo": [], "baseline": []},
        "D": {"ahorro": [], "consumo": [], "baseline": []},
    }
    
    errores_dict = {}
    
    # Abrir archivo CSV para guardar TODOS los valores de ahorro
    cdf_raw_file = Path(carpeta_salida) / "cdf_datos_brutos.csv"
    cdf_raw = open(cdf_raw_file, 'w', newline='', encoding='utf-8')
    cdf_writer = csv.writer(cdf_raw)
    cdf_writer.writerow(['config', 'ahorro'])
    
    print(f"\nAbriendo ZIP: {ruta_zip}")
    print("=" * 80)
    
    with zipfile.ZipFile(ruta_zip, 'r') as zf:
        # Encontrar todos los archivos .json
        archivos_rutas = [f for f in zf.namelist() if f.endswith('.json')]
        
        print(f"Encontrados {len(archivos_rutas)} archivos JSON")
        print("Procesando simulaciones...")
        print("=" * 80)
        
        errores = 0
        
        for idx, ruta_archivo in enumerate(archivos_rutas, 1):
            print(f"\r{mostrar_barra_progreso(idx, len(archivos_rutas))}", end=" | ", flush=True)
            print(f"📄 {Path(ruta_archivo).name[:50]}", end="\n")
            
            try:
                # Cargar datos desde ZIP
                rutas = cargar_rutas(ruta_archivo, zip_file=zf)
                
                # Calcular grid de tiempo
                T_max = max(
                    car["times"][-1][1]
                    for car_id, car in rutas.items()
                    if car_id.isdigit() and car.get("times")
                )
                time_grid = list(range(0, int(T_max) + 2))
                
                # Contar coches
                resultados_tiempos = contar_coches_todos_tiempos(rutas, time_grid)
                
                # Simular configuraciones
                config_baseline = CONFIGURACIONES["D"]
                
                for nombre, config in CONFIGURACIONES.items():
                    datos = simular_configuracion(
                        resultados_tiempos, config, config_baseline
                    )
                    
                    if "error" not in datos:
                        ahorro = datos.get("ahorro_porcentaje", 0)
                        acumuladores[nombre]["ahorro"].append(ahorro)
                        acumuladores[nombre]["consumo"].append(datos.get("consumo_total", 0))
                        acumuladores[nombre]["baseline"].append(datos.get("baseline_total", 0))
                        # Escribir cada valor al CSV de datos brutos
                        cdf_writer.writerow([nombre, ahorro])
                
            except Exception as e:
                errores += 1
                tipo_error = str(type(e).__name__)
                if tipo_error not in errores_dict:
                    errores_dict[tipo_error] = {"count": 0, "ejemplos": []}
                errores_dict[tipo_error]["count"] += 1
                if len(errores_dict[tipo_error]["ejemplos"]) < 3:
                    errores_dict[tipo_error]["ejemplos"].append({
                        "archivo": ruta_archivo,
                        "error": str(e)[:100]
                    })
                continue
    
    # Cerrar archivo CSV de datos brutos
    cdf_raw.close()
    print(f"\n✓ Datos brutos de CDF guardados en: {cdf_raw_file}")
    
    # Calcular estadísticas completas
    print("\n" + "=" * 80)
    print("ESTADÍSTICAS DETALLADAS")
    print("=" * 80)
    
    resultados_finales = []
    
    for config_name in ["A", "B", "C", "D"]:
        datos = acumuladores[config_name]
        if datos["ahorro"]:
            # Calcular todas las estadísticas
            ahorro_vals = datos["ahorro"]
            consumo_vals = datos["consumo"]
            baseline_vals = datos["baseline"]
            
            media_ahorro = sum(ahorro_vals) / len(ahorro_vals)
            media_consumo = sum(consumo_vals) / len(consumo_vals)
            media_baseline = sum(baseline_vals) / len(baseline_vals)
            
            desv_estandar = calcular_desv_estandar(ahorro_vals)
            ahorro_min = min(ahorro_vals)
            ahorro_max = max(ahorro_vals)
            p25 = calcular_percentil(ahorro_vals, 25)
            mediana = calcular_percentil(ahorro_vals, 50)
            p75 = calcular_percentil(ahorro_vals, 75)
            
            desc = CONFIGURACIONES[config_name]["descripcion"]
            print(f"\nConfig {config_name}: {desc}")
            print(f"  Simulaciones exitosas:    {len(ahorro_vals)}")
            print(f"  Ahorro medio:             {media_ahorro:.2f}%")
            print(f"  Desviación estándar:      {desv_estandar:.4f}")
            print(f"  Ahorro mínimo:            {ahorro_min:.2f}%")
            print(f"  Percentil 25:             {p25:.2f}%")
            print(f"  Mediana:                  {mediana:.2f}%")
            print(f"  Percentil 75:             {p75:.2f}%")
            print(f"  Ahorro máximo:            {ahorro_max:.2f}%")
            print(f"  Consumo medio:            {media_consumo:.6f}")
            print(f"  Baseline medio:           {media_baseline:.6f}")
            
            resultados_finales.append({
                "config": config_name,
                "descripcion": desc,
                "simulaciones_exitosas": len(ahorro_vals),
                "ahorro_medio_porcentaje": round(media_ahorro, 2),
                "desviacion_estandar": round(desv_estandar, 4),
                "ahorro_minimo_porcentaje": round(ahorro_min, 2),
                "percentil_25": round(p25, 2),
                "mediana_porcentaje": round(mediana, 2),
                "percentil_75": round(p75, 2),
                "ahorro_maximo_porcentaje": round(ahorro_max, 2),
                "consumo_medio": round(media_consumo, 6),
                "baseline_medio": round(media_baseline, 6),
                "total_archivos": len(archivos_rutas)
            })
    
    # Guardar resultado consolidado en CSV
    if resultados_finales:
        csv_file = Path(carpeta_salida) / "resultado_promedio.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=resultados_finales[0].keys())
            writer.writeheader()
            writer.writerows(resultados_finales)
        
        # También guardar en JSON
        json_file = Path(carpeta_salida) / "resultado_promedio.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(resultados_finales, f, indent=2)
        
        print(f"\n{'=' * 80}")
        print(f"✓ Resultados guardados en:")
        print(f"  📊 CSV:  {csv_file}")
        print(f"  📋 JSON: {json_file}")
        print(f"{'=' * 80}\n")
    
    if errores > 0:
        print(f"\n⚠ REPORTE DE ERRORES: {errores} archivos fallaron")
        print("=" * 80)
        for tipo_error, info in sorted(errores_dict.items(), key=lambda x: x[1]["count"], reverse=True):
            print(f"\n{tipo_error}: {info['count']} archivos")
            for ejemplo in info['ejemplos']:
                print(f"  - {ejemplo['archivo'][:60]}")
                print(f"    Error: {ejemplo['error']}")
    
    return resultados_finales


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python simulacion_batch_zip.py <ruta_zip> [carpeta_salida]")
        print("\nEjemplo:")
        print("  python simulacion_batch_zip.py datos.zip ../resultados")
        sys.exit(1)
    
    ruta_zip = sys.argv[1]
    carpeta_salida = sys.argv[2] if len(sys.argv) > 2 else "../resultados"
    
    procesar_zip(ruta_zip, carpeta_salida)
