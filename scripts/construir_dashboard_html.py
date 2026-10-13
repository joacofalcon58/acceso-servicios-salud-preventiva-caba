"""Genera el dashboard en HTML (index.html) con la misma información que el informe de Power BI.

Lee los archivos de data/raw y data/processed, calcula los indicadores por comuna, arma el mapa
en SVG a partir de los polígonos y escribe un único archivo index.html en la raíz del repositorio.

Antes de ejecutarlo hay que generar los indicadores de cobertura espacial y la sensibilidad del indicador:
    python scripts/analisis_acceso.py
    python scripts/sensibilidad_disponibilidad_relativa.py

Uso, desde la raíz del repositorio:
    python scripts/construir_dashboard_html.py
"""
import base64
import csv
import io
import json
import math
import sys
from datetime import date
from pathlib import Path

from PIL import Image
from shapely.geometry import shape

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import analisis_acceso as aa  # noqa: E402

RAIZ = AQUI.parent
RAW = RAIZ / "data" / "raw"
PROCESADO = RAIZ / "data" / "processed" / "acceso_comunas_exploratorio.csv"
SENSIBILIDAD = RAIZ / "data" / "processed" / "sensibilidad_disponibilidad_relativa.csv"
PLANTILLA = AQUI / "plantilla_dashboard.html"
PORTADA = RAIZ / "images" / "portada.png"
SALIDA = RAIZ / "index.html"

ESCALA = 5200.0  # píxeles por grado de latitud
TOLERANCIA = 0.00022  # simplificación de los polígonos, en grados (unos 25 metros)
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def simplificar(puntos, tol):
    """Douglas-Peucker sobre una lista de (x, y). Conserva el primer y el último punto."""
    if len(puntos) < 4:
        return puntos
    conservar = [False] * len(puntos)
    conservar[0] = conservar[-1] = True
    pila = [(0, len(puntos) - 1)]
    while pila:
        i, j = pila.pop()
        (x1, y1), (x2, y2) = puntos[i], puntos[j]
        dx, dy = x2 - x1, y2 - y1
        norma = math.hypot(dx, dy)
        maxd, idx = 0.0, None
        for k in range(i + 1, j):
            x, y = puntos[k]
            d = math.hypot(x - x1, y - y1) if norma == 0 else abs(dy * (x - x1) - dx * (y - y1)) / norma
            if d > maxd:
                maxd, idx = d, k
        if idx is not None and maxd > tol:
            conservar[idx] = True
            pila.append((i, idx))
            pila.append((idx, j))
    return [p for p, c in zip(puntos, conservar) if c]


def rangos_porcentuales(valores):
    """Posición relativa entre 0 y 1; los empates reciben el promedio de sus posiciones."""
    n = len(valores)
    resultado = []
    for v in valores:
        menores = sum(1 for w in valores if w < v)
        iguales = sum(1 for w in valores if w == v)
        resultado.append((menores + (iguales - 1) / 2) / (n - 1))
    return resultado


def fecha_larga(d):
    return f"{d.day} de {MESES[d.month - 1]} de {d.year}"


def main():
    estaciones = aa.leer_estaciones()
    poblacion = aa.leer_poblacion()
    poligonos = aa.leer_comunas()
    cobertura = {int(r["comuna"]): r for r in csv.DictReader(open(PROCESADO, encoding="utf-8-sig"))}
    barrios_poligono = {f["properties"]["comuna"]: f["properties"]["barrios"] for f in json.loads((RAW / "comunas.geojson").read_text(encoding="utf-8"))["features"]}

    servicios = sorted({s for e in estaciones for s in e["servicios"]}, key=lambda s: s.lower())
    indice_servicio = {s: i for i, s in enumerate(servicios)}
    total_servicios = len(servicios)

    # proyección a coordenadas de pantalla
    min_lon = min(p.bounds[0] for p in poligonos.values())
    max_lat = max(p.bounds[3] for p in poligonos.values())
    min_lat = min(p.bounds[1] for p in poligonos.values())
    max_lon = max(p.bounds[2] for p in poligonos.values())
    k_lon = math.cos(math.radians((min_lat + max_lat) / 2))
    margen = 12

    def proyectar(lon, lat):
        return ((lon - min_lon) * k_lon * ESCALA + margen, (max_lat - lat) * ESCALA + margen)

    ancho = (max_lon - min_lon) * k_lon * ESCALA + 2 * margen
    alto = (max_lat - min_lat) * ESCALA + 2 * margen

    # indicadores por comuna
    comunas = []
    por_comuna = {c: [e for e in estaciones if e["comuna"] == c] for c in poligonos}
    est100k, cob1000, diversidad = [], [], []
    orden_ids = sorted(poligonos)
    for c in orden_ids:
        n = len(por_comuna[c])
        est100k.append(n / poblacion[c]["poblacion"] * 1e5)
        cob1000.append(float(cobertura[c]["cobertura_1000m"]))
        diversidad.append(len(set().union(*[e["servicios"] for e in por_comuna[c]])) / total_servicios if n else 0.0)
    puntaje = [
        100 * sum(t) / 3
        for t in zip(rangos_porcentuales(est100k), rangos_porcentuales(cob1000), rangos_porcentuales(diversidad))
    ]
    redondeado = [round(p, 6) for p in puntaje]
    posicion = [1 + sum(1 for q in redondeado if q > r) for r in redondeado]

    for i, c in enumerate(orden_ids):
        pol = poligonos[c]
        partes = list(pol.geoms) if pol.geom_type == "MultiPolygon" else [pol]
        trazo = []
        for parte in partes:
            for anillo in [parte.exterior, *parte.interiors]:
                pts = [proyectar(x, y) for x, y in anillo.coords]
                pts = simplificar(pts, TOLERANCIA * ESCALA)
                trazo.append("M" + "L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z")
        punto = pol.centroid if pol.contains(pol.centroid) else pol.representative_point()
        cx, cy = proyectar(punto.x, punto.y)
        grupo = "Mayor disponibilidad relativa" if posicion[i] <= 5 else "Menor disponibilidad relativa" if posicion[i] >= 11 else "Disponibilidad relativa intermedia"
        comunas.append(
            {
                "id": c,
                "nombre": f"Comuna {c}",
                "corta": f"C{c}",
                "barrios": barrios_poligono[c],
                "poblacion": poblacion[c]["poblacion"],
                "superficie": poblacion[c]["superficie_km2"],
                "c500": float(cobertura[c]["cobertura_500m"]),
                "c1000": cob1000[i],
                "c2000": float(cobertura[c]["cobertura_2000m"]),
                "dist": float(cobertura[c]["distancia_media_m"]),
                "est100k": est100k[i],
                "diversidad": diversidad[i],
                "acceso": puntaje[i],
                "posicion": posicion[i],
                "grupo": grupo,
                "path": "".join(trazo),
                "cx": round(cx, 1),
                "cy": round(cy, 1),
            }
        )

    lista_estaciones = []
    for e in sorted(estaciones, key=lambda e: e["id"]):
        x, y = proyectar(e["lon"], e["lat"])
        lista_estaciones.append(
            {
                "id": e["id"],
                "nombre": e["nombre"],
                "tipo": e["tipo"],
                "estructura": e["estructura"],
                "direccion": e["direccion"],
                "barrio": e["barrio"],
                "comuna": e["comuna"],
                "servicios": sorted(indice_servicio[s] for s in e["servicios"]),
                "flag": e["bandera"],
                "x": round(x, 1),
                "y": round(y, 1),
            }
        )

    # porcentaje de combinaciones de pesos al azar en que cada comuna queda entre las cinco últimas
    with open(SENSIBILIDAD, encoding="utf-8-sig") as f:
        fila = next(r for r in csv.DictReader(f) if r["escenario"].startswith("Pesos al azar") and "últimas" in r["escenario"])
    estabilidad = {c: float(fila[f"posicion_comuna_{c}"]) for c in orden_ids}

    qa = armar_preguntas(comunas, lista_estaciones, servicios, estabilidad)
    datos = {
        "servicios": servicios,
        "estaciones": lista_estaciones,
        "comunas": comunas,
        "viewBox": [round(ancho), round(alto)],
        "qa": qa,
    }

    # portada reducida para no pasar de un par de cientos de kilobytes
    img = Image.open(PORTADA).convert("RGB")
    img.thumbnail((1600, 1600))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=82, optimize=True, progressive=True)
    portada = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()

    plantilla = PLANTILLA.read_text(encoding="utf-8")
    json_datos = json.dumps(datos, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = plantilla.replace("/*__DATOS__*/null", json_datos).replace("__PORTADA__", portada).replace("__FECHA__", fecha_larga(date.today()))
    SALIDA.write_text(html, encoding="utf-8")

    print("Archivo:", SALIDA.relative_to(RAIZ), "|", round(SALIDA.stat().st_size / 1024), "KB | portada", round(len(portada) / 1024), "KB | datos", round(len(json_datos) / 1024), "KB")
    print("Disponibilidad Relativa de la Oferta:", {c["id"]: (round(c["acceso"], 1), c["posicion"]) for c in comunas})


def armar_preguntas(comunas, estaciones, servicios, estabilidad):
    """Respuestas breves de las preguntas rápidas, con cifras calculadas desde los datos."""
    nf = lambda v: f"{v:,.0f}".replace(",", ".")
    nf2 = lambda v: f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    n = len(estaciones)
    fijas = [e for e in estaciones if e["tipo"] == "Fija"]
    moviles = [e for e in estaciones if e["tipo"] == "Móvil"]
    pob_total = sum(c["poblacion"] for c in comunas)
    solo_una = [c["id"] for c in comunas if sum(1 for e in estaciones if e["comuna"] == c["id"]) == 1]
    sin_fija = [c["id"] for c in comunas if not any(e["comuna"] == c["id"] and e["tipo"] == "Fija" for e in estaciones)]
    cuenta = lambda c: sum(1 for e in estaciones if e["comuna"] == c["id"])
    mayor = [c for c in comunas if c["posicion"] <= 5]
    menor = [c for c in comunas if c["posicion"] >= 11]
    grupo_est = lambda g: sum(cuenta(c) for c in g)
    grupo_pob = lambda g: sum(c["poblacion"] for c in g)
    lista = lambda g: ", ".join(str(c["id"]) for c in sorted(g, key=lambda c: c["id"]))
    estables = [c for c in menor if estabilidad[c["id"]] >= 85]
    inestables = [c for c in menor if estabilidad[c["id"]] < 85]
    est_max = max(comunas, key=lambda c: c["est100k"])
    est_min = min(comunas, key=lambda c: c["est100k"])

    cobertura_servicio = []
    for i, s in enumerate(servicios):
        comunas_con = {e["comuna"] for e in estaciones if i in e["servicios"]}
        cobertura_servicio.append((s, len(comunas_con), [c for c in sorted(comunas_con)]))
    gluc = next(x for x in cobertura_servicio if x[0] == "Control de Glucemia")
    basicos = next(x for x in cobertura_servicio if x[0] == "Control de Peso")

    def promedio(lst):
        d = [e for e in lst if e["flag"] != "SERVICIO_NULL"]
        return sum(len(e["servicios"]) for e in d) / len(d)

    return [
        {
            "q": "¿Hay estaciones en todas las comunas?",
            "a": f"Sí: las {len(comunas)} comunas tienen al menos una estación. Pero <b>{len(solo_una)} dependen de una sola</b> (comunas {', '.join(map(str, solo_una))}) y <b>{len(sin_fija)} no tienen ninguna fija</b> (comunas {', '.join(map(str, sin_fija))}): solo cuentan con estaciones móviles. Que figuren en el mapa no implica un acceso parejo.",
        },
        {
            "q": "¿Qué comunas tienen menos estaciones por habitante?",
            "a": f"La ciudad tiene <b>{nf2(n / pob_total * 1e5)}</b> estaciones cada 100.000 habitantes. Varía de <b>{nf2(est_min['est100k'])}</b> en la Comuna {est_min['id']} a <b>{nf2(est_max['est100k'])}</b> en la Comuna {est_max['id']}: más de tres veces. Es el cociente entre las estaciones de la comuna y su población del Censo 2022.",
        },
        {
            "q": "¿Qué servicios tienen menor cobertura territorial?",
            "a": f"Los controles básicos (por ejemplo, Control de Peso) llegan a <b>{basicos[1]} de {len(comunas)} comunas</b>. El Control de Glucemia llega a <b>{gluc[1]}</b> (comunas {', '.join(map(str, gluc[2]))}). Las Juegotecas y los Casilleros y Cambiadores están en una sola comuna. Una estación cercana no garantiza que ofrezca el servicio que se necesita.",
        },
        {
            "q": "¿Las estaciones móviles compensan las brechas?",
            "a": f"Amplían la presencia pero no la cartera de servicios. Las fijas ofrecen en promedio <b>{nf2(promedio(fijas)).replace(',00','')}</b> servicios y las móviles, <b>{nf2(promedio(moviles))}</b>. En las comunas {', '.join(map(str, sin_fija))} las móviles son la única presencia, y en dos de ellas hay una sola estación con dos servicios.",
        },
        {
            "q": "¿Qué comunas conviene analizar primero?",
            "a": f"Las cinco con menor disponibilidad relativa (<b>comunas {lista(menor)}</b>) suman {nf(grupo_pob(menor))} habitantes y {grupo_est(menor)} estaciones. Las cinco con mayor disponibilidad (comunas {lista(mayor)}) suman {nf(grupo_pob(mayor))} habitantes y {grupo_est(mayor)} estaciones. Al cambiar los pesos del indicador, las comunas {lista(estables)} siguen en el grupo de menor disponibilidad en más del 85 % de las pruebas; {'las comunas ' + lista(inestables) + ' solo en parte de ellas' if len(inestables) > 1 else 'la Comuna ' + lista(inestables) + ' solo en cerca de la mitad' if inestables else 'ninguna sale del grupo'}. La diferencia de estaciones entre los dos grupos es en parte esperable: las estaciones por habitante son uno de los tres componentes del indicador. Es una comparación exploratoria, no una medida de acceso efectivo.",
        },
        {
            "q": "¿Qué limitaciones tienen los datos?",
            "a": "No hay datos de <b>demanda, capacidad, horarios ni personas atendidas</b>, así que presencia no equivale a uso. Dos estaciones tienen el campo de servicios posiblemente truncado y una no informa servicios. La población es de 2022 y las estaciones, de 2026. La Disponibilidad Relativa de la Oferta es exploratoria: compara comunas entre sí. Ver las notas metodológicas al pie.",
        },
    ]


if __name__ == "__main__":
    main()
