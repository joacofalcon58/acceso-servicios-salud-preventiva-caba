"""Robustez del indicador Disponibilidad Relativa de la Oferta frente a decisiones metodológicas.

Compara el ordenamiento de las 15 comunas del indicador original (posiciones con
pesos iguales) con el que resulta de:

1. cambiar los pesos de los tres componentes;
2. quitar un componente por vez;
3. normalizar con mínimo-máximo o con puntaje z en lugar de posiciones;
4. sortear 20.000 combinaciones de pesos al azar;
5. suponer que las dos estaciones con el campo de servicios posiblemente truncado
   ofrecen más servicios que los registrados.

No reemplaza al indicador: mide cuánto dependen sus resultados de cada decisión.
Escribe data/processed/sensibilidad_disponibilidad_relativa.csv. Ver docs/metodologia.md.

Uso, desde la raíz del repositorio (después de analisis_acceso.py):
    python scripts/sensibilidad_disponibilidad_relativa.py
"""
import csv
import sys
from pathlib import Path

import numpy as np

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import analisis_acceso as aa  # noqa: E402

RAIZ = AQUI.parent
PROCESADO = RAIZ / "data" / "processed" / "acceso_comunas_exploratorio.csv"
SALIDA = RAIZ / "data" / "processed" / "sensibilidad_disponibilidad_relativa.csv"
COMPONENTES = ["estaciones_100k", "cobertura_1000m", "diversidad"]

sys.stdout.reconfigure(encoding="utf-8")


def minimo_maximo(valores):
    v = np.asarray(valores, dtype=float)
    return (v - v.min()) / (v.max() - v.min())


def puntaje_z(valores):
    v = np.asarray(valores, dtype=float)
    return (v - v.mean()) / v.std()


def posiciones(puntaje):
    """Posición 1 = mayor puntaje. Los empates comparten posición."""
    p = np.round(np.asarray(puntaje, dtype=float), 6)
    return np.array([1 + int((p > x).sum()) for x in p])


def tercio(posicion):
    return np.where(posicion <= 5, "mayor", np.where(posicion >= 11, "menor", "intermedia"))


def spearman(a, b):
    return float(np.corrcoef(aa.rangos_porcentuales(a), aa.rangos_porcentuales(b))[0, 1])


def kendall(a, b):
    """Tau-b de Kendall, con corrección por empates."""
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    concordantes = discordantes = empate_a = empate_b = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            s = np.sign(a[i] - a[j]) * np.sign(b[i] - b[j])
            if s > 0:
                concordantes += 1
            elif s < 0:
                discordantes += 1
            else:
                empate_a += a[i] == a[j] and b[i] != b[j]
                empate_b += b[i] == b[j] and a[i] != a[j]
    return (concordantes - discordantes) / np.sqrt(
        (concordantes + discordantes + empate_a) * (concordantes + discordantes + empate_b)
    )


def indice(matriz, normalizar, pesos):
    normalizada = np.column_stack([normalizar(matriz[:, j]) for j in range(matriz.shape[1])])
    return normalizada @ np.asarray(pesos, dtype=float)


def leer_componentes():
    filas = list(csv.DictReader(open(PROCESADO, encoding="utf-8-sig")))
    comunas = [int(f["comuna"]) for f in filas]
    matriz = np.array([[float(f[c]) for c in COMPONENTES] for f in filas])
    return comunas, matriz


def main():
    comunas, matriz = leer_componentes()
    tercios_iguales = [1 / 3, 1 / 3, 1 / 3]
    base = indice(matriz, aa.rangos_porcentuales, tercios_iguales)
    pos_base = posiciones(base)

    escenarios = [
        ("Original: posiciones, pesos iguales", aa.rangos_porcentuales, tercios_iguales, matriz),
        ("Pesos 50-25-25 (más peso a estaciones por habitante)", aa.rangos_porcentuales, [0.5, 0.25, 0.25], matriz),
        ("Pesos 25-50-25 (más peso a cobertura a 1.000 m)", aa.rangos_porcentuales, [0.25, 0.5, 0.25], matriz),
        ("Pesos 25-25-50 (más peso a diversidad)", aa.rangos_porcentuales, [0.25, 0.25, 0.5], matriz),
        ("Sin estaciones por habitante", aa.rangos_porcentuales, [0, 0.5, 0.5], matriz),
        ("Sin cobertura a 1.000 m", aa.rangos_porcentuales, [0.5, 0, 0.5], matriz),
        ("Sin diversidad", aa.rangos_porcentuales, [0.5, 0.5, 0], matriz),
        ("Normalización mínimo-máximo, pesos iguales", minimo_maximo, tercios_iguales, matriz),
        ("Normalización por puntaje z, pesos iguales", puntaje_z, tercios_iguales, matriz),
    ]

    # Truncamiento: Parque Avellaneda (Comuna 9) y Parque Los Andes (Comuna 15) pueden ofrecer
    # más servicios que los registrados. Se prueba con un servicio más y con la cartera más
    # amplia observada en la red (14 de 15, la unión de las estaciones fijas).
    total = len(set().union(*[e["servicios"] for e in aa.leer_estaciones()]))
    for nombre, valor in (("un servicio más", 11 / total), ("cartera fija completa (14 de 15)", 14 / total)):
        alterada = matriz.copy()
        for comuna in (9, 15):
            i = comunas.index(comuna)
            alterada[i, 2] = max(alterada[i, 2], valor)
        escenarios.append((f"Truncamiento: comunas 9 y 15 con {nombre}", aa.rangos_porcentuales, tercios_iguales, alterada))

    filas = []
    print("escenario | Spearman | Kendall | mayor cambio de posición | comunas que cambian de tercio")
    for nombre, normalizar, pesos, datos in escenarios:
        puntaje = indice(datos, normalizar, pesos)
        pos = posiciones(puntaje)
        cambian = [c for c, a, b in zip(comunas, tercio(pos_base), tercio(pos)) if a != b]
        rho, tau = spearman(base, puntaje), kendall(base, puntaje)
        print(nombre, "|", round(rho, 2), "|", round(tau, 2), "|", int(np.abs(pos - pos_base).max()), "|", cambian or "ninguna")
        fila = {
            "escenario": nombre,
            "spearman": round(rho, 3),
            "kendall": round(tau, 3),
            "mayor_cambio_posicion": int(np.abs(pos - pos_base).max()),
            "comunas_cambian_tercio": " ".join(map(str, cambian)),
        }
        fila.update({f"posicion_comuna_{c}": int(p) for c, p in zip(comunas, pos)})
        filas.append(fila)

    # Pesos al azar: con qué frecuencia cada comuna queda en el tercio superior o inferior.
    generador = np.random.default_rng(aa.SEMILLA)
    pesos = generador.dirichlet(np.ones(len(COMPONENTES)), size=aa.SORTEOS_PESOS)
    rangos = np.column_stack([aa.rangos_porcentuales(matriz[:, j]) for j in range(matriz.shape[1])])
    sorteos = (-(pesos @ rangos.T)).argsort(axis=1).argsort(axis=1) + 1
    print(f"\n{aa.SORTEOS_PESOS} combinaciones de pesos al azar")
    print("comuna | posición original | rango del 5 al 95 % | % en las cinco primeras | % en las cinco últimas")
    for i, c in enumerate(comunas):
        p = sorteos[:, i]
        print(c, "|", pos_base[i], "|", f"{int(np.percentile(p, 5))} a {int(np.percentile(p, 95))}", "|", f"{(p <= 5).mean():.0%}", "|", f"{(p >= 11).mean():.0%}")
    fila = {"escenario": f"Pesos al azar: % de {aa.SORTEOS_PESOS} sorteos en las cinco últimas", "spearman": "", "kendall": "", "mayor_cambio_posicion": "", "comunas_cambian_tercio": ""}
    fila.update({f"posicion_comuna_{c}": round(float((sorteos[:, i] >= 11).mean()) * 100, 1) for i, c in enumerate(comunas)})
    filas.append(fila)
    fila = {"escenario": f"Pesos al azar: % de {aa.SORTEOS_PESOS} sorteos en las cinco primeras", "spearman": "", "kendall": "", "mayor_cambio_posicion": "", "comunas_cambian_tercio": ""}
    fila.update({f"posicion_comuna_{c}": round(float((sorteos[:, i] <= 5).mean()) * 100, 1) for i, c in enumerate(comunas)})
    filas.append(fila)

    with open(SALIDA, "w", encoding="utf-8-sig", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0]))
        escritor.writeheader()
        escritor.writerows(filas)
    print("\nArchivo escrito:", SALIDA.relative_to(RAIZ))


if __name__ == "__main__":
    main()
