import csv
import json
import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None


def leer_cdf_csv(ruta_csv):
    ruta_csv = Path(ruta_csv)
    if not ruta_csv.exists():
        raise FileNotFoundError(f"No se encontró el archivo CDF: {ruta_csv}")

    datos = []
    with ruta_csv.open("r", encoding="utf-8", newline="") as f:
        lector = csv.DictReader(f)
        for fila in lector:
            datos.append({
                "config": fila["config"],
                "ahorro": float(fila["ahorro"]),
                "cdf": float(fila.get("cdf", 0.0)),  # Si no existe, asignar 0.0
            })
    return datos


def leer_resultados_json(ruta_directorio):
    ruta_directorio = Path(ruta_directorio)
    if not ruta_directorio.exists():
        raise FileNotFoundError(f"No existe la carpeta de resultados: {ruta_directorio}")

    datos = []
    archivos = sorted(ruta_directorio.glob("*_resultados.json"))
    if not archivos:
        raise FileNotFoundError(f"No se encontraron archivos '*_resultados.json' en {ruta_directorio}")

    for archivo in archivos:
        with archivo.open("r", encoding="utf-8") as f:
            contenido = json.load(f)
            resultados = contenido.get("resultados") or {}
            for config, resumen in resultados.items():
                if "ahorro_porcentaje" in resumen:
                    datos.append({
                        "config": config,
                        "ahorro": float(resumen["ahorro_porcentaje"]),
                        "cdf": 0.0,
                    })
    return datos


def calcular_cdf(datos):
    # Ordenar y calcular CDF por configuración
    por_config = {}
    for fila in datos:
        por_config.setdefault(fila["config"], []).append(fila["ahorro"])

    resultado = []
    for config, valores in por_config.items():
        valores_ordenados = sorted(valores)
        total = len(valores_ordenados)
        for idx, valor in enumerate(valores_ordenados, start=1):
            resultado.append({
                "config": config,
                "ahorro": float(valor),
                "cdf": idx / total,
            })
    return sorted(resultado, key=lambda x: (x["config"], x["ahorro"]))


def guardar_cdf_por_configuracion(datos, ruta_salida):
    ruta_salida = Path(ruta_salida)
    ruta_salida.mkdir(parents=True, exist_ok=True)

    archivo_salida = ruta_salida / "cdf_ahorro_por_configuracion.csv"
    with archivo_salida.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.writer(f)
        escritor.writerow(["config", "ahorro", "cdf"])
        for fila in datos:
            escritor.writerow([fila["config"], f"{fila["ahorro"]:.6f}", f"{fila["cdf"]:.6f}"])

    return archivo_salida


def generar_grafico_cdf(datos, ruta_salida):
    if plt is None:
        return None

    configs = sorted(set(fila["config"] for fila in datos))
    fig, ax = plt.subplots(figsize=(8, 5))

    for config in configs:
        valores = [fila for fila in datos if fila["config"] == config]
        x = [fila["ahorro"] for fila in valores]
        y = [fila["cdf"] for fila in valores]
        ax.step(x, y, where="post", label=config)

    ax.set_xlabel("Ahorro energético (%)")
    ax.set_ylabel("CDF")
    ax.set_title("CDF del ahorro energético por configuración")
    ax.legend(title="Configuración")
    ax.grid(True, linestyle="--", alpha=0.5)

    salida_png = Path(ruta_salida) / "cdf_ahorro.png"
    fig.tight_layout()
    try:
        fig.savefig(salida_png, dpi=150)
        plt.close(fig)
        return salida_png
    except PermissionError:
        plt.close(fig)
        print(f"⚠ No hay permisos para guardar en: {salida_png}")
        return None
    except Exception as e:
        plt.close(fig)
        print(f"⚠ Error al guardar gráfico: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 generar_cdf.py <entrada> [carpeta_salida]")
        print("Donde <entrada> puede ser:")
        print("  - cdf_datos_brutos.csv (desde simulacion_batch_zip.py) [RECOMENDADO]")
        print("  - una carpeta con archivos '*_resultados.json'")
        print("Ejemplo: python3 generar_cdf.py ../resultados/cdf_datos_brutos.csv ../resultados")
        sys.exit(1)

    ruta_entrada = Path(sys.argv[1])
    carpeta_salida = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("../resultados")

    # Primero intenta leer cdf_datos_brutos.csv (tiene TODOS los valores)
    cdf_brutos = Path(carpeta_salida) / "cdf_datos_brutos.csv"
    if cdf_brutos.exists():
        print(f"Leyendo datos brutos desde: {cdf_brutos}")
        datos = leer_cdf_csv(cdf_brutos)
    elif ruta_entrada.is_dir():
        print(f"Leyendo archivos de resultados desde: {ruta_entrada}")
        datos = leer_resultados_json(ruta_entrada)
    elif ruta_entrada.suffix.lower() == ".csv":
        print(f"Leyendo CSV desde: {ruta_entrada}")
        datos = leer_cdf_csv(ruta_entrada)
    else:
        raise ValueError("La entrada debe ser una carpeta de resultados o un archivo CSV de CDF.")

    datos_cdf = calcular_cdf(datos)
    ruta_salida = guardar_cdf_por_configuracion(datos_cdf, carpeta_salida)

    print(f"✓ Archivo CDF generado en: {ruta_salida}")
    print(f"  Total de valores procesados: {len(datos_cdf)}")
    print("Cada fila tiene: config, ahorro, cdf")

    grafico = generar_grafico_cdf(datos_cdf, carpeta_salida)
    if grafico:
        print(f"✓ Gráfico generado en: {grafico}")
    else:
        print("⚠ matplotlib no está instalado; solo se ha generado el CSV de datos CDF.")


if __name__ == "__main__":
    main()
