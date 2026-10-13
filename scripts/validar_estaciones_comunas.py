"""Valida que cada Estación Saludable caiga dentro de la comuna y del barrio que declara.

Compara el punto del GeoJSON de estaciones contra los polígonos de comunas del
Gobierno de la Ciudad (data/raw/comunas.geojson). No modifica ningún archivo.

Uso, desde la raíz del repositorio:
    python scripts/validar_estaciones_comunas.py
"""
import json
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw"

sys.stdout.reconfigure(encoding="utf-8")


def normalizar(texto):
    """Minúsculas, sin tildes ni espacios sobrantes, para comparar nombres de barrio."""
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(sin_tildes.lower().split())


def punto_en_anillo(x, y, anillo):
    """Algoritmo de trazado de rayos para un anillo de coordenadas (lon, lat)."""
    dentro = False
    n = len(anillo)
    j = n - 1
    for i in range(n):
        xi, yi = anillo[i][0], anillo[i][1]
        xj, yj = anillo[j][0], anillo[j][1]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            dentro = not dentro
        j = i
    return dentro


def punto_en_poligono(x, y, poligono):
    """El primer anillo es el exterior; los siguientes son huecos."""
    if not punto_en_anillo(x, y, poligono[0]):
        return False
    return not any(punto_en_anillo(x, y, hueco) for hueco in poligono[1:])


def punto_en_geometria(x, y, geometria):
    if geometria["type"] == "Polygon":
        return punto_en_poligono(x, y, geometria["coordinates"])
    return any(punto_en_poligono(x, y, p) for p in geometria["coordinates"])


def main():
    comunas = json.loads((RAW / "comunas.geojson").read_text(encoding="utf-8"))["features"]
    estaciones = json.loads((RAW / "estaciones_saludables.geo.json").read_text(encoding="utf-8"))["features"]

    fuera = 0
    distinta_comuna = 0
    barrio_no_listado = 0
    print("id | estación | comuna declarada | comuna por polígono | barrio declarado | resultado")
    for est in estaciones:
        p = est["properties"]
        lon, lat = est["geometry"]["coordinates"]
        declarada = int(p["comuna"].split()[1])
        halladas = [c["properties"]["comuna"] for c in comunas if punto_en_geometria(lon, lat, c["geometry"])]
        observaciones = []
        if not halladas:
            fuera += 1
            observaciones.append("FUERA DE CABA")
        elif declarada not in halladas:
            distinta_comuna += 1
            observaciones.append("COMUNA DISTINTA")
        if halladas:
            barrios = {normalizar(b) for b in next(c for c in comunas if c["properties"]["comuna"] == halladas[0])["properties"]["barrios"].split(",")}
            if normalizar(p["barrio"]) not in barrios:
                barrio_no_listado += 1
                observaciones.append("BARRIO NO LISTADO EN LA COMUNA")
        print(p["id"], "|", p["nombre"], "|", declarada, "|", halladas or "-", "|", p["barrio"], "|", ", ".join(observaciones) or "OK")

    print()
    print("Estaciones:", len(estaciones))
    print("Fuera de CABA:", fuera)
    print("Comuna declarada distinta de la del polígono:", distinta_comuna)
    print("Barrio no listado en la comuna del polígono:", barrio_no_listado)


if __name__ == "__main__":
    main()
