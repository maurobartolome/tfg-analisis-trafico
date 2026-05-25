import math
import random
from cargar_datos import cargar_rutas, cargar_mapa
from contar_datos import contar_coches_todos_tiempos

# ─────────────────────────────────────────────
# PARÁMETROS FÍSICOS (Capa PHY, μ=2)
# ─────────────────────────────────────────────

MU          = 2
SCS_HZ      = 12 * 60e3               # = 720 kHz por RB
T_SIMBOLO_S = 1e-3 / (14 * (2**MU))  # = 17.857 μs
T_SLOT_MS   = 14 * T_SIMBOLO_S * 1e3 # = 0.25 ms
PDB_MS      = 5.0                     # ms
S           = math.floor(PDB_MS / T_SLOT_MS)  # = 20 slots
G           = 222                     # RBs totales del canal
BITRATE_BPS = 25e6                    # 25 Mbps por coche
SE          = 3.9023                  # MCS 21, 64-QAM, URLLC

# ─────────────────────────────────────────────
# TAMAÑO DEL FRAME (distribución gamma mixta)
# Tabla II del paper de referencia
# ─────────────────────────────────────────────

# Media teórica E[F] de la mezcla de gammas
F_bits = (1/12 * 16.487 * 21499 +   # Frame tipo I (keyframe)
          5/12 * 15.584 * 14608 +   # Frame tipo B (bidireccional)
          6/12 * 17     * 15895)    # Frame tipo P (predictivo)

# Función para samplear un frame aleatorio
def generar_frame_bits():
    """
    Genera el tamaño de un frame según la mezcla de
    distribuciones gamma de la Tabla II del paper.
    Usa aproximación de gamma mediante suma de exponenciales.
    """
    # Elegir tipo de frame con probabilidades
    rand = random.random()
    if rand < 1/12:
        tipo = 'I'
        alpha, beta = 16.487, 21499
    elif rand < (1/12 + 5/12):
        tipo = 'B'
        alpha, beta = 15.584, 14608
    else:
        tipo = 'P'
        alpha, beta = 17, 15895
    
    # Generar gamma usando suma de exponenciales (método de Marsaglia-Tsang simplificado)
    # Aproximación: gamma(alpha, beta) ≈ beta * sum(exp(-random()) for i in range(int(alpha)))
    suma = sum(-math.log(random.random()) for _ in range(int(alpha)))
    return beta * suma

# ─────────────────────────────────────────────
# PARÁMETROS DERIVADOS
# ─────────────────────────────────────────────

# Bits por RB por símbolo y por slot
b_simbolo = SCS_HZ * SE * T_SIMBOLO_S   # bits/RB/símbolo
b_slot    = b_simbolo * 14               # bits/RB/slot

# RBs necesarios para transmitir F_bits en 1 slot
R = math.ceil(F_bits / b_slot)

print("="*60)
print("PARÁMETROS FÍSICOS")
print("="*60)
print(f"T_símbolo:              {T_SIMBOLO_S*1e6:.2f} μs")
print(f"T_slot:                 {T_SLOT_MS:.3f} ms")
print(f"Slots en PDB (S):       {S}")
print(f"SE (MCS 21):            {SE}")
print(f"bits/RB/símbolo:        {b_simbolo:.2f}")
print(f"bits/RB/slot:           {b_slot:.2f}")
print(f"E[F] frame medio:       {F_bits:.0f} bits")
print(f"RBs necesarios (R):     {R}")

# ─────────────────────────────────────────────
# CONSUMO NORMALIZADO (paper Kairos, Tabla I)
# ─────────────────────────────────────────────

P_ACTIVA = 1.000
P_ASM1   = 0.675  # switching 37μs
P_ASM2   = 0.550  # switching 0.5ms
P_ASM3   = 0.230  # switching 5ms

# Consumo medio en transición (valor medio entre activo y ASM)
P_TRANS_ASM1 = (P_ACTIVA + P_ASM1) / 2  # = 0.8375
P_TRANS_ASM2 = (P_ACTIVA + P_ASM2) / 2  # = 0.7750
P_TRANS_ASM3 = (P_ACTIVA + P_ASM3) / 2  # = 0.6150

# Switching delay en slots (redondeado al alza)
SW_ASM1_SLOTS = math.ceil(0.037  / T_SLOT_MS)  # 37μs  → 1 slot
SW_ASM2_SLOTS = math.ceil(0.5    / T_SLOT_MS)  # 0.5ms → 2 slots
SW_ASM3_SLOTS = math.ceil(5.0    / T_SLOT_MS)  # 5ms   → 20 slots

# ─────────────────────────────────────────────
# CONFIGURACIONES DE BWP
# ─────────────────────────────────────────────

CONFIGURACIONES = {
    "D": {
        "n_bwps":      24,
        "bwp_size":     9,
        "asm":        P_ACTIVA,
        "p_trans":    P_ACTIVA,
        "sw_slots":   0,
        "descripcion": "Baseline (24 BWPs × 9 RBs, FDM puro)"
    },
    "A": {
        "n_bwps":       6,
        "bwp_size":    36,
        "asm":        P_ASM1,
        "p_trans":    P_TRANS_ASM1,
        "sw_slots":   SW_ASM1_SLOTS,
        "descripcion": "Adaptada P50 (6 BWPs × 36 RBs, ASM1)"
    },
    "B": {
        "n_bwps":       2,
        "bwp_size":   111,
        "asm":        P_ASM2,
        "p_trans":    P_TRANS_ASM2,
        "sw_slots":   SW_ASM2_SLOTS,
        "descripcion": "Adaptada P90 (2 BWPs × 111 RBs, ASM2)"
    },
"C": {
    "n_bwps":       1,
    "bwp_size":   222,
    "asm":        P_ASM2,      # ← cambia ASM3 por ASM2
    "p_trans":    P_TRANS_ASM2, # ← cambia también la transición
    "sw_slots":   SW_ASM2_SLOTS, # ← 2 slots en lugar de 20
    "descripcion": "Ráfaga máxima (1 BWP × 222 RBs, ASM2)"
},
}

# ─────────────────────────────────────────────
# LÓGICA DE LA SIMULACIÓN
# ─────────────────────────────────────────────

def calcular_consumo_instante(n_coches: int, config: dict) -> float:
    """
    Calcula el consumo normalizado de la gNB en un instante.

    Ciclo de S=20 slots:
        sc_total  → slots transmitiendo (activos)
        sw_slots  → slots en transición (entrada + salida)
        sleep     → slots en ASM puro

    consumo = (sc/S)×P_activa + (sw/S)×P_trans + (sleep/S)×P_ASM
    """
    if n_coches == 0:
        return 0.0

    n_bwps   = config["n_bwps"]
    bwp_size = config["bwp_size"]
    p_asm    = config["asm"]
    p_trans  = config["p_trans"]
    sw_slots = config["sw_slots"]

    # Slots necesarios para transmitir (1 coche en su BWP)
    sc_1coche = math.ceil(R / bwp_size)

    # Si hay más coches que BWPs → TDM
    factor_tdm = math.ceil(n_coches / n_bwps)
    sc_total   = min(sc_1coche * factor_tdm, S)

    # Slots de transición (entrada + salida del ASM)
    slots_trans = min(2 * sw_slots, S - sc_total)

    # Slots en ASM puro
    slots_sleep = max(S - sc_total - slots_trans, 0)

    # Fracciones de tiempo
    f_activo = sc_total    / S
    f_trans  = slots_trans / S
    f_sleep  = slots_sleep / S

    return f_activo * P_ACTIVA + f_trans * p_trans + f_sleep * p_asm


def simular_configuracion(contar_tiempos: dict,
                          config: dict,
                          config_baseline: dict) -> dict:
    consumo_total  = 0.0
    baseline_total = 0.0
    n_instantes    = 0

    for tiempo, calles in contar_tiempos.items():
        for calle, n_coches in calles.items():
            if n_coches == 0:
                continue
            consumo_total  += calcular_consumo_instante(n_coches, config)
            baseline_total += calcular_consumo_instante(n_coches,
                                                        config_baseline)
            n_instantes    += 1

    if n_instantes == 0:
        return {"error": "Sin tráfico"}

    ahorro = 1 - (consumo_total / baseline_total)

    return {
        "consumo_total":       round(consumo_total, 4),
        "baseline_total":      round(baseline_total, 4),
        "ahorro_porcentaje":   round(ahorro * 100, 2),
        "instantes_evaluados": n_instantes,
    }


def comparar_configuraciones(contar_tiempos: dict) -> None:
    config_baseline = CONFIGURACIONES["D"]

    print("\n" + "="*60)
    print("SIMULACIÓN DE AHORRO ENERGÉTICO")
    print(f"SE={SE} | R={R} RBs | S={S} slots | E[F]={F_bits:.0f} bits")
    print("="*60)

    for nombre, config in CONFIGURACIONES.items():
        datos = simular_configuracion(
            contar_tiempos, config, config_baseline
        )
        sc_1 = math.ceil(R / config["bwp_size"])
        sw   = config["sw_slots"]
        print(f"\n── Config {nombre}: {config['descripcion']} ──")
        print(f"  Sc (1 coche):         {sc_1} slots")
        print(f"  Switching delay:      {sw} slots")
        print(f"  ASM consumo:          {config['asm']}")
        print(f"  Transición consumo:   {config['p_trans']}")
        print(f"  Instantes evaluados:  {datos['instantes_evaluados']}")
        print(f"  Consumo normalizado:  {datos['consumo_total']}")
        print(f"  Baseline (Config D):  {datos['baseline_total']}")
        print(f"  Ahorro vs baseline:   {datos['ahorro_porcentaje']} %")


# ─────────────────────────────────────────────
# EJECUCIÓN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    rutas = cargar_rutas()
    mapa  = cargar_mapa()

    T_max = max(
        car["times"][-1][1]
        for car_id, car in rutas.items()
        if car_id.isdigit()
    )
    time_grid = list(range(0, int(T_max) + 2))

    resultados = contar_coches_todos_tiempos(rutas, time_grid)
    comparar_configuraciones(resultados)