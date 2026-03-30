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


def riv_por_calle_instante(n_coches: int, N_BWP: int, rbs_por_coche: int) -> list[dict]:
    """
    Todos los coches reciben siempre el mismo L_RBs fijo.
    La BWP activa se reduce si hay menos coches → ahorro energético.

    Ejemplo con rbs_por_coche=24:
        1 coche  → BWP_activa=24,  L_RBs=24
        5 coches → BWP_activa=120, L_RBs=24
        9 coches → BWP_activa=216, L_RBs=24
    """
    if n_coches == 0:
        return []

    bwp_activa = seleccionar_bwp(n_coches, rbs_por_coche, N_BWP)

    configs = []
    for i in range(n_coches):
        rb_start = i * rbs_por_coche
        if rb_start + rbs_por_coche > bwp_activa:
            break
        riv = calcular_riv(bwp_activa, rb_start, rbs_por_coche)
        configs.append({
            "vehiculo_idx": i,
            "RB_start":     rb_start,
            "L_RBs":        rbs_por_coche,   # ← siempre igual
            "RIV":          riv,
            "BWP_activa":   bwp_activa,
        })
    return configs


def calcular_riv_simulacion(contar_tiempos: dict, N_BWP: int = 222, rbs_por_coche: int = 24) -> dict:
    """
    :param contar_tiempos: {tiempo: {calle_tuple: n_coches}}
    :param N_BWP:          tamaño total del canal en RBs (222 = 160 MHz μ=2)
    :param rbs_por_coche:  RBs fijos asignados a cada vehículo
    :return:               {tiempo: {calle_tuple: [configs_riv]}}
    """
    resultado = {}
    for tiempo, calles in contar_tiempos.items():
        resultado[tiempo] = {}
        for calle, n_coches in calles.items():
            resultado[tiempo][calle] = riv_por_calle_instante(n_coches, N_BWP, rbs_por_coche)
    return resultado