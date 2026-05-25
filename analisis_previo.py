from cargar_datos import cargar_rutas, cargar_mapa
from contar_datos import contar_coches_todos_tiempos


# ─────────────────────────────────────────────
# 0. Parámetros del canal
# ─────────────────────────────────────────────

N_RB_TOTAL = 222   # RBs en 160 MHz con μ=2


# ─────────────────────────────────────────────
# 1. Análisis del mapa: capacidades teóricas
# ─────────────────────────────────────────────

mapa = cargar_mapa()
max_todeds = [link['max_toded'] for link in mapa['links']]

max_toded_global = max(max_todeds)
rbs_por_coche = N_RB_TOTAL // max_toded_global

print("="*60)
print("ANÁLISIS DEL MAPA")
print("="*60)
print(f"Número de calles:        {len(max_todeds)}")
print(f"max_toded mínimo:        {min(max_todeds)}")
print(f"max_toded máximo:        {max_toded_global}")
print(f"max_toded medio:         {sum(max_todeds)/len(max_todeds):.2f}")
print(f"max_toded mediana:       {sorted(max_todeds)[len(max_todeds)//2]}")
print()
print(f"RBs por coche derivados: {rbs_por_coche}")
print(f"  (={N_RB_TOTAL}/{max_toded_global}, peor caso del mapa)")


# ─────────────────────────────────────────────
# 2. Análisis del tráfico: ocupación real
# ─────────────────────────────────────────────

rutas = cargar_rutas()
T_max = max(car["times"][-1][1] for car_id, car in rutas.items() if car_id.isdigit())
time_grid = list(range(0, int(T_max) + 2))
resultados = contar_coches_todos_tiempos(rutas, time_grid)

ocupacion_max_por_calle = {}
for tiempo, calles in resultados.items():
    for calle, n in calles.items():
        if calle not in ocupacion_max_por_calle:
            ocupacion_max_por_calle[calle] = 0
        if n > ocupacion_max_por_calle[calle]:
            ocupacion_max_por_calle[calle] = n

print("\n" + "="*60)
print("ANÁLISIS DEL TRÁFICO")
print("="*60)
ocupaciones_max = list(ocupacion_max_por_calle.values())
print(f"Calles con tráfico:           {len(ocupaciones_max)}")
print(f"Ocupación máxima absoluta:    {max(ocupaciones_max)}")
print(f"Ocupación media (de máximos): {sum(ocupaciones_max)/len(ocupaciones_max):.2f}")


# ─────────────────────────────────────────────
# 3. Distribución de demanda en RBs
# ─────────────────────────────────────────────

demandas = []
for tiempo, calles in resultados.items():
    for calle, n in calles.items():
        if n > 0:
            demandas.append(n * rbs_por_coche)

print("\n" + "="*60)
print(f"DEMANDA DE RBs (con {rbs_por_coche} RBs/coche)")
print("="*60)
print(f"Demanda mínima:  {min(demandas)} RBs ({min(demandas)/N_RB_TOTAL*100:.1f}% del canal)")
print(f"Demanda máxima:  {max(demandas)} RBs ({max(demandas)/N_RB_TOTAL*100:.1f}% del canal)")
print(f"Demanda media:   {sum(demandas)/len(demandas):.1f} RBs")

demandas_ordenadas = sorted(demandas)
n = len(demandas_ordenadas)
print(f"\nPercentiles de demanda:")
for p in [25, 50, 75, 90, 95, 99]:
    idx = int(n * p / 100)
    valor = demandas_ordenadas[idx]
    print(f"  P{p}: {valor} RBs ({valor/N_RB_TOTAL*100:.1f}% del canal)")