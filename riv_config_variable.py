import math

def calcular_riv(N_BWP: int, rb_start: int, L_RBs: int) -> int:
    """RIV según 3GPP TS 38.214 §5.1.2.2.2"""
    if not (1 <= L_RBs <= N_BWP - rb_start):
        raise ValueError(f"Asignación inválida: rb_start={rb_start}, L_RBs={L_RBs}, N_BWP={N_BWP}")
    if (L_RBs - 1) <= math.floor(N_BWP / 2):
        return N_BWP * (L_RBs - 1) + rb_start
    else:
        return N_BWP * (N_BWP - L_RBs + 1) + (N_BWP - 1 - rb_start)


def seleccionar_bwp(n_coches: int, rbs_por_coche: int, N_BWP_total: int) -> int:
    """BWP activa mínima necesaria para los coches presentes."""
    return min(n_coches * rbs_por_coche, N_BWP_total)


def riv_por_calle_instante(n_coches: int, N_BWP: int) -> list[dict]:
    """
    Los RBs por coche varían según cuántos coches hay en la celda.
    Con pocos coches cada uno recibe más RBs → más capacidad.
    Con muchos coches cada uno recibe menos RBs → se reparte el canal.

    Ejemplo con N_BWP=222:
        1 coche  → L_RBs=222, BWP_activa=222
        5 coches → L_RBs=44,  BWP_activa=220
        9 coches → L_RBs=24,  BWP_activa=216
    """
    if n_coches == 0:
        return []

    L_RBs = max(N_BWP // n_coches, 1)      # ← cambia según n_coches
    bwp_activa = seleccionar_bwp(n_coches, L_RBs, N_BWP)

    configs = []
    for i in range(n_coches):
        rb_start = i * L_RBs
        if rb_start + L_RBs > bwp_activa:
            break
        riv = calcular_riv(bwp_activa, rb_start, L_RBs)
        configs.append({
            "vehiculo_idx": i,
            "RB_start":     rb_start,
            "L_RBs":        L_RBs,          # ← varía por calle e instante
            "RIV":          riv,
            "BWP_activa":   bwp_activa,
        })
    return configs


def calcular_riv_simulacion(contar_tiempos: dict, N_BWP: int = 222) -> dict:
    """
    :param contar_tiempos: {tiempo: {calle_tuple: n_coches}}
    :param N_BWP:          tamaño total del canal en RBs (222 = 160 MHz μ=2)
    :return:               {tiempo: {calle_tuple: [configs_riv]}}
    """
    resultado = {}
    for tiempo, calles in contar_tiempos.items():
        resultado[tiempo] = {}
        for calle, n_coches in calles.items():
            resultado[tiempo][calle] = riv_por_calle_instante(n_coches, N_BWP)
    return resultado