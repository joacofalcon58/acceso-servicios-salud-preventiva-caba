"""Análisis exploratorio del acceso a Estaciones Saludables por comuna.

Calcula, para las 15 comunas, los indicadores normalizados por población y
superficie, la cobertura espacial por radio y la sensibilidad de un indicador
compuesto a distintos pesos. No modifica las fuentes: escribe un único archivo
en data/processed/.

Los resultados son exploratorios. Ver docs/metodologia.md.

Uso, desde la raíz del repositorio:
    python scripts/analisis_acceso.py
"""
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np
import openpyxl
from shapely import contains_xy
from shapely.geometry import shape

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw"
SALIDA = RAIZ / "data" / "processed" / "acceso_comunas_exploratorio.csv"

sys.stdout.reconfigure(encoding="utf-8")

RADIOS_M = (500, 1000, 2000)
PASO_GRILLA_M = 50
SERVICIO_BASICO = "Control de Presión Arterial"
SERVICIO_ESCASO = "Control de Glucemia"
SEMILLA = 20261005
SORTEOS_PESOS = 20000
LIMITE_BYTES_SERVICIO = 254

# Aproximación local de grados a metros para la latitud de la ciudad.
LAT_REF = -34.6
M_POR_GRADO_LAT = 110_574.0
M_POR_GRADO_LON = 111_320.0 * np.cos(np.radians(LAT_REF))


def leer_estaciones():
    """Atributos del CSV y coordenadas del GeoJSON, unidos por id."""
    filas = list(csv.DictReader(open(RAW / "estaciones_saludables.csv", encoding="utf-8-sig")))
    geo = json.loads((RAW / "estaciones_saludables.geo.json").read_text(encoding="utf-8"))["features"]
    coords = {str(f["properties"]["id"]): f["geometry"]["coordinates"] for f in geo}

    todos = [[s.strip() for s in f["servicio"].split(" - ")] if f["servicio"] else [] for f in filas]
    confirmados = set()
    for f, lista in zip(filas, todos):
        truncada = f["servicio"] and len(f["servicio"].encode("utf-8")) >= LIMITE_BYTES_SERVICIO
        confirmados.update(lista[:-1] if truncada else lista)

    estaciones = []
    for f, lista in zip(filas, todos):
        truncada = f["servicio"] and len(f["servicio"].encode("utf-8")) >= LIMITE_BYTES_SERVICIO
        if truncada and lista and lista[-1] not in confirmados:
            lista = lista[:-1]
        lon, lat = coords[f["id"]]
        if not f["servicio"]:
            bandera = "SERVICIO_NULL"
        elif truncada:
            bandera = "POSIBLE_TRUNCAMIENTO"
        else:
            bandera = "OK"
        estaciones.append(
            {
                "id": int(f["id"]),
                "nombre": f["nombre"],
                "tipo": f["tipo"],
                "estructura": f["estructura"],
                "direccion": f["direccion"],
                "barrio": f["barrio"],
                "comuna": int(f["comuna"].split()[1]),
                "servicios": set(lista),
                "bandera": bandera,
                "lon": lon,
                "lat": lat,
            }
        )
    return estaciones


def leer_poblacion():
    """Población y superficie oficial (Cuadro 2.1) y población de 65 y más (Cuadro 5.1)."""
    limpiar = lambda v: "" if v is None else str(v).replace("\xa0", " ").strip()

    libro = openpyxl.load_workbook(RAW / "c2022_caba_est_c2_1.xlsx", data_only=True)
    hoja = [h for h in libro.worksheets if h.title.replace("\xa0", " ") == "Cuadro 2.1"][0]
    datos = {}
    for fila in hoja.iter_rows(values_only=True):
        if limpiar(fila[1]).startswith("Comuna "):
            comuna = int(limpiar(fila[1]).split()[1])
            datos[comuna] = {"superficie_km2": float(fila[2]), "poblacion": int(float(fila[3]))}

    libro = openpyxl.load_workbook(RAW / "c2022_caba_est_c5_1.xlsx", data_only=True)
    for hoja in libro.worksheets[3:]:
        comuna = int(re.search(r"Comuna (\d+)", limpiar(hoja.cell(2, 1).value)).group(1))
        mayores = 0
        for fila in hoja.iter_rows(values_only=True):
            etiqueta = limpiar(fila[0])
            if etiqueta.startswith("100 y"):
                mayores += int(fila[1])
            elif re.fullmatch(r"\d+-\d+", etiqueta) and int(etiqueta.split("-")[0]) >= 65:
                mayores += int(fila[1])
        datos[comuna]["poblacion_65_mas"] = mayores
    return datos


def leer_comunas():
    geo = json.loads((RAW / "comunas.geojson").read_text(encoding="utf-8"))["features"]
    return {f["properties"]["comuna"]: shape(f["geometry"]) for f in geo}


def distancias_m(lon, lat, puntos_lon, puntos_lat):
    """Distancia en metros de cada punto de la grilla a cada estación (matriz puntos x estaciones)."""
    dx = (lon[None, :] - puntos_lon[:, None]) * M_POR_GRADO_LON
    dy = (lat[None, :] - puntos_lat[:, None]) * M_POR_GRADO_LAT
    return np.hypot(dx, dy)


def cobertura_espacial(poligono, estaciones, servicio=None):
    """Porcentaje de la superficie de la comuna a menos de cada radio de una estación, y distancia media."""
    elegidas = [e for e in estaciones if servicio is None or servicio in e["servicios"]]
    minx, miny, maxx, maxy = poligono.bounds
    xs = np.arange(minx, maxx, PASO_GRILLA_M / M_POR_GRADO_LON)
    ys = np.arange(miny, maxy, PASO_GRILLA_M / M_POR_GRADO_LAT)
    X, Y = np.meshgrid(xs, ys)
    X, Y = X.ravel(), Y.ravel()
    dentro = contains_xy(poligono, X, Y)
    X, Y = X[dentro], Y[dentro]
    lon = np.array([e["lon"] for e in elegidas])
    lat = np.array([e["lat"] for e in elegidas])
    mas_cercana = distancias_m(lon, lat, X, Y).min(axis=1)
    resultado = {f"cobertura_{r}m": float((mas_cercana <= r).mean()) for r in RADIOS_M}
    resultado["distancia_media_m"] = float(mas_cercana.mean())
    return resultado


def rangos_porcentuales(valores):
    """Posición relativa entre 0 y 1; los empates reciben el promedio de sus posiciones."""
    valores = np.asarray(valores, dtype=float)
    orden = valores.argsort(kind="stable")
    rangos = np.empty(len(valores))
    rangos[orden] = np.arange(len(valores))
    for v in np.unique(valores):
        rangos[valores == v] = rangos[valores == v].mean()
    return rangos / (len(valores) - 1)


def sensibilidad(titulo, componentes, filas, pesos_azar=True):
    """Puntaje de cada comuna con pesos iguales y, opcionalmente, con pesos al azar."""
    matriz = np.array([[f[c] for c in componentes] for f in filas])
    rangos = np.column_stack([rangos_porcentuales(matriz[:, j]) for j in range(len(componentes))])
    puntaje = rangos.mean(axis=1) * 100
    posicion = (-puntaje).argsort().argsort() + 1
    print(f"\n{titulo}: {', '.join(componentes)}")
    if not pesos_azar:
        print("com | puntaje con pesos iguales | posición")
        for i, f in enumerate(filas):
            print(f["comuna"], "|", round(puntaje[i], 1), "|", posicion[i])
        return
    generador = np.random.default_rng(SEMILLA)
    pesos = generador.dirichlet(np.ones(len(componentes)), size=SORTEOS_PESOS)
    posiciones = (-(pesos @ rangos.T)).argsort(axis=1).argsort(axis=1) + 1
    print("posición 1 = mayor disponibilidad relativa")
    print("com | puntaje con pesos iguales | posición | mediana con pesos al azar | rango del 5 al 95 % | prob. de estar entre las 3 últimas")
    for i, f in enumerate(filas):
        p = posiciones[:, i]
        ultimas = (p >= len(filas) - 2).mean()
        print(f["comuna"], "|", round(puntaje[i], 1), "|", posicion[i], "|", int(np.median(p)), "|", f"{int(np.percentile(p, 5))}-{int(np.percentile(p, 95))}", "|", f"{ultimas:.0%}")


def main():
    estaciones = leer_estaciones()
    poblacion = leer_poblacion()
    poligonos = leer_comunas()
    total_servicios = len(set().union(*[e["servicios"] for e in estaciones]))

    filas = []
    for comuna in sorted(poligonos):
        propias = [e for e in estaciones if e["comuna"] == comuna]
        pob = poblacion[comuna]
        n = len(propias)
        relaciones = sum(len(e["servicios"]) for e in propias)
        diversidad = len(set().union(*[e["servicios"] for e in propias])) / total_servicios if propias else 0.0
        fila = {
            "comuna": comuna,
            "poblacion": pob["poblacion"],
            "superficie_km2": pob["superficie_km2"],
            "poblacion_65_mas": pob["poblacion_65_mas"],
            "estaciones": n,
            "fijas": sum(e["tipo"] == "Fija" for e in propias),
            "moviles": sum(e["tipo"] == "Móvil" for e in propias),
            "estaciones_100k": n / pob["poblacion"] * 100_000,
            "habitantes_por_estacion": pob["poblacion"] / n,
            "estaciones_km2": n / pob["superficie_km2"],
            "relaciones_servicio": relaciones,
            "servicios_100k": relaciones / pob["poblacion"] * 100_000,
            "diversidad": diversidad,
        }
        punto = poligonos[comuna].centroid
        if not poligonos[comuna].contains(punto):
            punto = poligonos[comuna].representative_point()
        fila["centroide_latitud"] = punto.y
        fila["centroide_longitud"] = punto.x
        cualquiera = cobertura_espacial(poligonos[comuna], estaciones)
        fila.update({k: v for k, v in cualquiera.items()})
        basico = cobertura_espacial(poligonos[comuna], estaciones, SERVICIO_BASICO)
        fila["cobertura_1000m_presion"] = basico["cobertura_1000m"]
        escaso = cobertura_espacial(poligonos[comuna], estaciones, SERVICIO_ESCASO)
        fila["cobertura_2000m_glucemia"] = escaso["cobertura_2000m"]
        filas.append(fila)

    campos = list(filas[0])
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    with open(SALIDA, "w", encoding="utf-8-sig", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        escritor.writeheader()
        for fila in filas:
            escritor.writerow({k: (round(v, 4) if isinstance(v, float) else v) for k, v in fila.items()})

    print("Indicadores por comuna")
    encabezado = ["com", "est", "est/100k", "hab/est", "est/km2", "serv/100k", "divers", "cob500", "cob1000", "cob2000", "dist_media", "cob1000_PA", "cob2000_gluc"]
    print(" | ".join(encabezado))
    for f in filas:
        print(
            f["comuna"], "|", f["estaciones"], "|", round(f["estaciones_100k"], 2), "|", round(f["habitantes_por_estacion"]),
            "|", round(f["estaciones_km2"], 3), "|", round(f["servicios_100k"], 1), "|", round(f["diversidad"], 3),
            "|", round(f["cobertura_500m"], 3), "|", round(f["cobertura_1000m"], 3), "|", round(f["cobertura_2000m"], 3),
            "|", round(f["distancia_media_m"]), "|", round(f["cobertura_1000m_presion"], 3), "|", round(f["cobertura_2000m_glucemia"], 3),
        )

    candidatos = ["estaciones_100k", "estaciones_km2", "cobertura_1000m", "diversidad", "servicios_100k"]
    seleccion = ["estaciones_100k", "cobertura_1000m", "diversidad"]

    matriz = np.array([[f[c] for c in candidatos] for f in filas])
    rangos = np.column_stack([rangos_porcentuales(matriz[:, j]) for j in range(len(candidatos))])

    print("\nCorrelación de Spearman entre componentes candidatos (15 comunas)")
    correlacion = np.corrcoef(rangos.T)
    print("               " + " ".join(f"{c[:12]:>12}" for c in candidatos))
    for i, c in enumerate(candidatos):
        print(f"{c[:14]:<14} " + " ".join(f"{correlacion[i, j]:>12.2f}" for j in range(len(candidatos))))

    sensibilidad("Los cinco componentes candidatos", candidatos, filas)
    sensibilidad("Los tres componentes elegidos", seleccion, filas)
    for quitado in seleccion:
        sensibilidad(f"Los tres componentes elegidos, sin {quitado}", [c for c in seleccion if c != quitado], filas, pesos_azar=False)

    print("\nArchivo escrito:", SALIDA.relative_to(RAIZ))


if __name__ == "__main__":
    main()
