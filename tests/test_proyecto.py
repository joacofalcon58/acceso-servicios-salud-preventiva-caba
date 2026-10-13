"""Pruebas automatizadas del proyecto.

Recalculan los indicadores desde los archivos de data/raw con una implementación
propia, que no importa los scripts del proyecto, y los comparan con:

- los valores de referencia documentados;
- data/processed/acceso_comunas_exploratorio.csv (salida de scripts/analisis_acceso.py);
- los datos incrustados en index.html (salida de scripts/construir_dashboard_html.py);
- las definiciones del modelo de Power BI (archivos TMDL).

La cobertura espacial se verifica con un método distinto del que usa el proyecto:
unión geométrica de círculos sobre el elipsoide WGS84 en lugar de una grilla de puntos.

Uso, desde la raíz del repositorio:
    python -m unittest discover -s tests -v
"""
import csv
import json
import math
import re
import subprocess
import unittest
from pathlib import Path

import openpyxl
from shapely.geometry import Point, shape
from shapely.ops import transform, unary_union

RAIZ = Path(__file__).resolve().parent.parent
RAW = RAIZ / "data" / "raw"
PROCESADO = RAIZ / "data" / "processed" / "acceso_comunas_exploratorio.csv"
SENSIBILIDAD = RAIZ / "data" / "processed" / "sensibilidad_acceso_relativo.csv"
MODELO = RAIZ / "powerbi" / "acceso-servicios-salud-caba.SemanticModel" / "definition"
LIMITE_BYTES = 254  # largo máximo de un campo de texto en formato Shapefile


# ---------------------------------------------------------------- lectura independiente
def leer_csv(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def leer_estaciones():
    filas = leer_csv(RAW / "estaciones_saludables.csv")
    listas = {f["id"]: [s.strip() for s in f["servicio"].split(" - ") if s.strip()] for f in filas}
    truncada = {f["id"]: len(f["servicio"].encode("utf-8")) >= LIMITE_BYTES for f in filas}
    confirmados = set()
    for i, lista in listas.items():
        confirmados.update(lista[:-1] if truncada[i] else lista)
    for f in filas:
        lista = listas[f["id"]]
        if truncada[f["id"]] and lista and lista[-1] not in confirmados:
            lista = lista[:-1]
        f["servicios"] = set(lista)
        f["numero_comuna"] = int(f["comuna"].split()[1])
        f["sin_dato"] = f["servicio"] == ""
        f["truncada"] = truncada[f["id"]]
    return filas


def leer_puntos():
    geo = json.loads((RAW / "estaciones_saludables.geo.json").read_text(encoding="utf-8"))
    return geo, {str(f["properties"]["id"]): tuple(f["geometry"]["coordinates"]) for f in geo["features"]}


def leer_comunas():
    geo = json.loads((RAW / "comunas.geojson").read_text(encoding="utf-8"))
    return geo, {f["properties"]["comuna"]: shape(f["geometry"]) for f in geo["features"]}


def leer_poblacion():
    limpiar = lambda v: "" if v is None else str(v).replace("\xa0", " ").strip()
    libro = openpyxl.load_workbook(RAW / "c2022_caba_est_c2_1.xlsx", data_only=True)
    hoja = [h for h in libro.worksheets if h.title.replace("\xa0", " ") == "Cuadro 2.1"][0]
    poblacion, superficie, total = {}, {}, None
    for fila in hoja.iter_rows(values_only=True):
        if limpiar(fila[1]).startswith("Comuna "):
            comuna = int(limpiar(fila[1]).split()[1])
            superficie[comuna], poblacion[comuna] = float(fila[2]), int(float(fila[3]))
        elif limpiar(fila[1]) == "Total":
            total = int(float(fila[3]))
    return poblacion, superficie, total


def posicion_relativa(valores):
    """Posición entre 0 y 1; los empates reciben el promedio. Implementación por ordenamiento."""
    orden = sorted(valores)
    n = len(valores)
    resultado = []
    for v in valores:
        primero = orden.index(v)
        ultimo = n - 1 - orden[::-1].index(v)
        resultado.append((primero + ultimo) / 2 / (n - 1))
    return resultado


def proyeccion_local(lat0=-34.615, lon0=-58.445):
    """Metros por grado sobre el elipsoide WGS84 en la latitud de la ciudad."""
    a, f = 6378137.0, 1 / 298.257223563
    e2 = f * (2 - f)
    seno2 = math.sin(math.radians(lat0)) ** 2
    meridiano = a * (1 - e2) / (1 - e2 * seno2) ** 1.5
    vertical = a / math.sqrt(1 - e2 * seno2)
    kx = math.radians(1) * vertical * math.cos(math.radians(lat0))
    ky = math.radians(1) * meridiano
    return lambda x, y, z=None: ((x - lon0) * kx, (y - lat0) * ky)


def datos_del_dashboard():
    html = (RAIZ / "index.html").read_text(encoding="utf-8")
    inicio = html.index("const D = ") + len("const D = ")
    datos, _ = json.JSONDecoder().raw_decode(html[inicio:])
    return datos


# ---------------------------------------------------------------- datos compartidos
ESTACIONES = leer_estaciones()
GEO_ESTACIONES, PUNTOS = leer_puntos()
GEO_COMUNAS, POLIGONOS = leer_comunas()
POBLACION, SUPERFICIE, TOTAL_CENSO = leer_poblacion()
COMUNAS = sorted(POLIGONOS)
CATALOGO = sorted(set().union(*[e["servicios"] for e in ESTACIONES]))
FIJAS = [e for e in ESTACIONES if e["tipo"] == "Fija"]
MOVILES = [e for e in ESTACIONES if e["tipo"] == "Móvil"]
PROCESADO_FILAS = {int(f["comuna"]): f for f in leer_csv(PROCESADO)}


def promedio_servicios(estaciones):
    con_dato = [e for e in estaciones if not e["sin_dato"]]
    return sum(len(e["servicios"]) for e in con_dato) / len(con_dato)


def componentes():
    cantidad = {c: sum(e["numero_comuna"] == c for e in ESTACIONES) for c in COMUNAS}
    por_habitante = [cantidad[c] / POBLACION[c] * 100_000 for c in COMUNAS]
    cobertura = [float(PROCESADO_FILAS[c]["cobertura_1000m"]) for c in COMUNAS]
    diversidad = [
        len(set().union(*[e["servicios"] for e in ESTACIONES if e["numero_comuna"] == c])) / len(CATALOGO) for c in COMUNAS
    ]
    return cantidad, por_habitante, cobertura, diversidad


def acceso_relativo():
    _, por_habitante, cobertura, diversidad = componentes()
    partes = [posicion_relativa(v) for v in (por_habitante, cobertura, diversidad)]
    puntaje = [100 * sum(t) / 3 for t in zip(*partes)]
    redondeado = [round(p, 6) for p in puntaje]
    posicion = [1 + sum(q > p for q in redondeado) for p in redondeado]
    return puntaje, posicion


# ---------------------------------------------------------------- pruebas
class IntegridadDeFuentes(unittest.TestCase):
    def test_cantidad_e_identificadores(self):
        self.assertEqual(len(ESTACIONES), 25)
        ids = [e["id"] for e in ESTACIONES]
        self.assertEqual(len(set(ids)), 25, "hay identificadores de estación repetidos")
        self.assertEqual(set(ids), set(PUNTOS), "el CSV y el GeoJSON no tienen las mismas estaciones")
        self.assertEqual(len({e["nombre"] for e in ESTACIONES}), 25, "hay nombres de estación repetidos")

    def test_campos_obligatorios_sin_nulos(self):
        for campo in ("id", "nombre", "tipo", "estructura", "direccion", "barrio", "comuna"):
            self.assertTrue(all(e[campo].strip() for e in ESTACIONES), f"hay valores vacíos en {campo}")
        self.assertEqual({e["tipo"] for e in ESTACIONES}, {"Fija", "Móvil"})

    def test_csv_y_geojson_tienen_los_mismos_atributos_y_coordenadas(self):
        por_id = {e["id"]: e for e in ESTACIONES}
        for f in GEO_ESTACIONES["features"]:
            p, e = f["properties"], por_id[str(f["properties"]["id"])]
            for campo in ("nombre", "tipo", "estructura", "direccion", "barrio", "comuna"):
                self.assertEqual(p[campo], e[campo])
            self.assertEqual(p["servicio"] or "", e["servicio"])
            lon, lat = map(float, re.match(r"POINT \(([-\d.]+) ([-\d.]+)\)", e["geometry"]).groups())
            self.assertAlmostEqual(lon, f["geometry"]["coordinates"][0], places=9)
            self.assertAlmostEqual(lat, f["geometry"]["coordinates"][1], places=9)

    def test_sistema_de_referencia_y_rango_de_coordenadas(self):
        for geo in (GEO_ESTACIONES, GEO_COMUNAS):
            self.assertIn("CRS84", geo["crs"]["properties"]["name"])
        min_lon, min_lat, max_lon, max_lat = unary_union(list(POLIGONOS.values())).bounds
        for lon, lat in PUNTOS.values():
            self.assertTrue(min_lon <= lon <= max_lon and min_lat <= lat <= max_lat, "estación fuera del recuadro de la ciudad")

    def test_cada_estacion_cae_en_la_comuna_que_declara(self):
        for e in ESTACIONES:
            punto = Point(PUNTOS[e["id"]])
            contienen = [c for c, poligono in POLIGONOS.items() if poligono.contains(punto)]
            self.assertEqual(contienen, [e["numero_comuna"]], e["nombre"])

    def test_poligonos_de_comunas(self):
        self.assertEqual(COMUNAS, list(range(1, 16)))
        self.assertTrue(all(p.is_valid for p in POLIGONOS.values()))
        solape = sum(POLIGONOS[a].intersection(POLIGONOS[b]).area for a in COMUNAS for b in COMUNAS if a < b)
        self.assertAlmostEqual(solape, 0, places=10, msg="los polígonos de comunas se superponen")

    def test_poblacion_del_censo(self):
        self.assertEqual(sorted(POBLACION), COMUNAS)
        self.assertEqual(sum(POBLACION.values()), 3_121_707)
        self.assertEqual(sum(POBLACION.values()), TOTAL_CENSO, "la suma de comunas no coincide con el total del cuadro")
        self.assertTrue(all(v > 0 for v in POBLACION.values()) and all(v > 0 for v in SUPERFICIE.values()))


class Servicios(unittest.TestCase):
    def test_calidad_del_campo_servicio(self):
        self.assertEqual([e["nombre"] for e in ESTACIONES if e["sin_dato"]], ["Estación Saludable Plaza Houssay"])
        self.assertEqual(
            sorted(e["nombre"] for e in ESTACIONES if e["truncada"]),
            ["Estación Saludable Parque Avellaneda", "Estación Saludable Parque Los Andes"],
        )

    def test_tabla_puente_sin_duplicados(self):
        for e in ESTACIONES:
            lista = [s.strip() for s in e["servicio"].split(" - ") if s.strip()]
            self.assertEqual(len(lista), len(set(lista)), f"servicio repetido en {e['nombre']}")
        self.assertEqual(sum(len(e["servicios"]) for e in ESTACIONES), 191)

    def test_indicadores_de_referencia(self):
        self.assertEqual(len(FIJAS), 17)
        self.assertEqual(len(MOVILES), 8)
        self.assertEqual(len({e["numero_comuna"] for e in ESTACIONES}), 15)
        self.assertEqual(len(CATALOGO), 15)
        self.assertAlmostEqual(promedio_servicios(ESTACIONES), 7.9583, places=4)
        self.assertAlmostEqual(promedio_servicios(FIJAS), 10.0, places=4)
        self.assertAlmostEqual(promedio_servicios(MOVILES), 3.875, places=4)
        self.assertEqual(len(set().union(*[e["servicios"] for e in FIJAS])), 14)
        self.assertEqual(len(set().union(*[e["servicios"] for e in MOVILES])), 7)

    def test_presencia_por_tipo(self):
        con_fijas = {e["numero_comuna"] for e in FIJAS}
        con_moviles = {e["numero_comuna"] for e in MOVILES}
        self.assertEqual((len(con_fijas), len(con_moviles)), (12, 6))
        self.assertEqual(sorted(con_moviles - con_fijas), [1, 10, 13])
        una_sola = [c for c in COMUNAS if sum(e["numero_comuna"] == c for e in ESTACIONES) == 1]
        self.assertEqual(una_sola, [1, 4, 5, 9, 10, 11, 15])

    def test_cobertura_territorial_por_servicio(self):
        comunas_con = lambda s: sorted({e["numero_comuna"] for e in ESTACIONES if s in e["servicios"]})
        esperado = {
            "Actividad Física": 14,
            "Asesoría Nutricional": 13,
            "Control de Peso": 13,
            "Control de Presión Arterial": 13,
            "Control de Talla": 13,
            "Servicios de Enfermería": 12,
            "Cumpleaños Saludables": 11,
            "Taller Cognitivo": 11,
            "Talleres Literarios": 11,
            "Talleres de Escritura": 11,
            "Talleres para Ejercitar tu Mente": 6,
            "Control de Glucemia": 2,
            "Actividades para Adultos Mayores": 2,
            "Actividades para Niños (Juegotecas)": 1,
            "Casilleros y Cambiadores": 1,
        }
        self.assertEqual({s: len(comunas_con(s)) for s in CATALOGO}, esperado)
        self.assertEqual(comunas_con("Control de Glucemia"), [5, 9])
        self.assertEqual(sum(esperado.values()), 134, "celdas con servicio en la matriz de servicio por comuna")


class IndicadoresPorComuna(unittest.TestCase):
    def test_totales_de_la_ciudad(self):
        self.assertAlmostEqual(25 / sum(POBLACION.values()) * 100_000, 0.8008, places=4)
        self.assertEqual(round(sum(POBLACION.values()) / 25), 124_868)

    def test_archivo_procesado_coincide_con_el_recalculo(self):
        cantidad, por_habitante, _, diversidad = componentes()
        for i, c in enumerate(COMUNAS):
            fila = PROCESADO_FILAS[c]
            self.assertEqual(int(fila["poblacion"]), POBLACION[c])
            self.assertEqual(int(fila["estaciones"]), cantidad[c])
            self.assertAlmostEqual(float(fila["estaciones_100k"]), por_habitante[i], places=4)
            self.assertAlmostEqual(float(fila["habitantes_por_estacion"]), POBLACION[c] / cantidad[c], places=3)
            self.assertAlmostEqual(float(fila["diversidad"]), diversidad[i], places=4)

    def test_extremos_de_estaciones_por_habitante(self):
        _, por_habitante, _, _ = componentes()
        valores = dict(zip(COMUNAS, por_habitante))
        self.assertEqual(max(valores, key=valores.get), 6)
        self.assertEqual(min(valores, key=valores.get), 4)
        self.assertAlmostEqual(valores[6], 1.48, places=2)
        self.assertAlmostEqual(valores[4], 0.44, places=2)
        self.assertGreater(valores[6] / valores[4], 3)


class CoberturaEspacial(unittest.TestCase):
    """Verifica la grilla del proyecto contra la unión geométrica de círculos en metros."""

    @classmethod
    def setUpClass(cls):
        proyectar = proyeccion_local()
        cls.poligonos = {c: transform(proyectar, p) for c, p in POLIGONOS.items()}
        puntos = [transform(proyectar, Point(xy)) for xy in PUNTOS.values()]
        cls.areas = {r: unary_union([p.buffer(r, quad_segs=64) for p in puntos]) for r in (500, 1000, 2000)}

    def test_cobertura_por_comuna(self):
        for radio, cubierta in self.areas.items():
            for c in COMUNAS:
                exacta = self.poligonos[c].intersection(cubierta).area / self.poligonos[c].area
                grilla = float(PROCESADO_FILAS[c][f"cobertura_{radio}m"])
                self.assertAlmostEqual(grilla, exacta, delta=0.005, msg=f"comuna {c}, {radio} m")

    def test_cobertura_de_la_ciudad(self):
        ciudad = unary_union(list(self.poligonos.values()))
        exacta = ciudad.intersection(self.areas[1000]).area / ciudad.area
        ponderada = sum(float(PROCESADO_FILAS[c]["cobertura_1000m"]) * SUPERFICIE[c] for c in COMUNAS) / sum(SUPERFICIE.values())
        self.assertAlmostEqual(exacta, 0.356, delta=0.002)
        self.assertAlmostEqual(ponderada, exacta, delta=0.003)

    def test_la_union_no_cuenta_dos_veces_las_superposiciones(self):
        suma_de_circulos = 25 * math.pi * 1000**2
        self.assertLess(self.areas[1000].area, suma_de_circulos)

    def test_superficie_de_los_poligonos(self):
        total = sum(p.area for p in self.poligonos.values()) / 1e6
        declarada = sum(f["properties"]["area"] for f in GEO_COMUNAS["features"]) / 1e6
        self.assertAlmostEqual(total, declarada, delta=0.1, msg="la proyección local no reproduce el área publicada")


class AccesoRelativo(unittest.TestCase):
    def test_puntajes_y_posiciones_documentados(self):
        puntaje, posicion = acceso_relativo()
        esperado = {1: (3.6, 15), 2: (71.4, 3), 3: (73.8, 2), 4: (21.4, 13), 5: (69.0, 5), 6: (97.6, 1), 7: (64.3, 6), 8: (61.9, 7),
                    9: (33.3, 11), 10: (20.2, 14), 11: (31.0, 12), 12: (71.4, 3), 13: (42.9, 9), 14: (52.4, 8), 15: (35.7, 10)}
        self.assertEqual({c: (round(p, 1), q) for c, p, q in zip(COMUNAS, puntaje, posicion)}, esperado)

    def test_escala_y_grupos(self):
        puntaje, posicion = acceso_relativo()
        self.assertTrue(all(0 <= p <= 100 for p in puntaje))
        self.assertEqual(sum(q <= 5 for q in posicion), 5)
        self.assertEqual(sum(q >= 11 for q in posicion), 5)

    def test_grupos_extremos_con_poblacion_similar(self):
        _, posicion = acceso_relativo()
        cantidad, _, _, _ = componentes()
        mayor = [c for c, q in zip(COMUNAS, posicion) if q <= 5]
        menor = [c for c, q in zip(COMUNAS, posicion) if q >= 11]
        self.assertEqual((sum(POBLACION[c] for c in mayor), sum(cantidad[c] for c in mayor)), (992_086, 10))
        self.assertEqual((sum(POBLACION[c] for c in menor), sum(cantidad[c] for c in menor)), (999_462, 5))

    def test_la_diversidad_tiene_pocos_valores_distintos(self):
        """Limitación documentada: nueve comunas empatan, así que un servicio de diferencia mueve mucho la posición."""
        _, _, _, diversidad = componentes()
        self.assertEqual(sorted({round(d * len(CATALOGO)) for d in diversidad}), [2, 7, 10, 11])
        self.assertEqual(sum(round(d * len(CATALOGO)) == 10 for d in diversidad), 9)

    def test_archivo_de_sensibilidad(self):
        filas = leer_csv(SENSIBILIDAD)
        _, posicion = acceso_relativo()
        original = filas[0]
        self.assertTrue(original["escenario"].startswith("Original"))
        self.assertEqual([int(original[f"posicion_comuna_{c}"]) for c in COMUNAS], posicion)
        for fila in filas:
            if fila["spearman"]:
                self.assertEqual(int(fila["posicion_comuna_6"]), 1, fila["escenario"])
                self.assertEqual(int(fila["posicion_comuna_1"]), 15, fila["escenario"])
                self.assertGreaterEqual(float(fila["spearman"]), 0.9, fila["escenario"])


class DashboardHtml(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.datos = datos_del_dashboard()

    def test_estaciones_y_servicios(self):
        self.assertEqual(len(self.datos["estaciones"]), 25)
        self.assertEqual(sorted(self.datos["servicios"], key=str.lower), sorted(CATALOGO, key=str.lower))
        por_id = {e["id"]: e for e in ESTACIONES}
        for e in self.datos["estaciones"]:
            fuente = por_id[str(e["id"])]
            self.assertEqual((e["nombre"], e["tipo"], e["comuna"]), (fuente["nombre"], fuente["tipo"], fuente["numero_comuna"]))
            self.assertEqual({self.datos["servicios"][i] for i in e["servicios"]}, fuente["servicios"])

    def test_indicadores_por_comuna(self):
        puntaje, posicion = acceso_relativo()
        _, por_habitante, cobertura, diversidad = componentes()
        por_id = {c["id"]: c for c in self.datos["comunas"]}
        for i, c in enumerate(COMUNAS):
            d = por_id[c]
            self.assertEqual(d["poblacion"], POBLACION[c])
            self.assertAlmostEqual(d["est100k"], por_habitante[i], places=6)
            self.assertAlmostEqual(d["c1000"], cobertura[i], places=6)
            self.assertAlmostEqual(d["diversidad"], diversidad[i], places=6)
            self.assertAlmostEqual(d["acceso"], puntaje[i], places=6)
            self.assertEqual(d["posicion"], posicion[i])

    def test_la_pagina_declara_que_es_un_proyecto_independiente(self):
        html = (RAIZ / "index.html").read_text(encoding="utf-8")
        self.assertTrue("proyecto analítico independiente" in html.lower(), "falta el aviso de proyecto independiente")
        self.assertTrue("no es un producto oficial" in html.lower(), "falta aclarar que no es un producto oficial")
        self.assertTrue('<html lang="es">' in html, "falta el idioma del documento")


class ModeloPowerBI(unittest.TestCase):
    def test_sin_rutas_locales(self):
        texto = (MODELO / "expressions.tmdl").read_text(encoding="utf-8")
        self.assertNotRegex(texto, r"(?i)c:\\users\\")

    def test_medidas_de_red_completa_quitan_todos_los_filtros_de_estacion(self):
        columnas = re.findall(r"^\tcolumn (\w+)", (MODELO / "tables" / "Dim_Estacion.tmdl").read_text(encoding="utf-8"), flags=re.M)
        medidas = (MODELO / "tables" / "_Medidas.tmdl").read_text(encoding="utf-8")
        for nombre in ("Estaciones cada 100.000 habitantes (red completa)", "Diversidad Servicios (red completa)"):
            cuerpo = medidas.split(f"measure '{nombre}' =")[1].split("lineageTag")[0]
            for columna in columnas:
                if columna in ("comuna", "numero_comuna"):  # deben conservar el filtro de comuna
                    self.assertNotIn(f"Dim_Estacion[{columna}]", cuerpo)
                else:
                    self.assertIn(f"REMOVEFILTERS(Dim_Estacion[{columna}])", cuerpo, f"{nombre}: falta {columna}")
            self.assertIn("REMOVEFILTERS(Dim_Servicio)", cuerpo)

    def test_relaciones_de_filtro_simple(self):
        texto = (MODELO / "relationships.tmdl").read_text(encoding="utf-8")
        self.assertEqual(texto.count("relationship "), 3)
        self.assertNotIn("crossFilteringBehavior", texto, "hay una relación bidireccional")


class Repositorio(unittest.TestCase):
    def test_enlaces_locales_del_readme_y_la_documentacion(self):
        for archivo in [RAIZ / "README.md", *sorted((RAIZ / "docs").glob("*.md"))]:
            texto = archivo.read_text(encoding="utf-8")
            for destino in re.findall(r"\]\((?!https?:|#|mailto:)([^)#]+)(?:#[^)]*)?\)", texto):
                self.assertTrue((archivo.parent / destino).exists(), f"{archivo.name}: enlace roto a {destino}")

    def test_archivos_versionados(self):
        salida = subprocess.run(["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8")
        if salida.returncode != 0:
            self.skipTest("no es un repositorio git")
        archivos = salida.stdout.splitlines()
        self.assertFalse([a for a in archivos if a.lower().endswith((".pdf", ".pbix", ".abf"))])
        self.assertFalse([a for a in archivos if "localSettings.json" in a or "__pycache__" in a])


if __name__ == "__main__":
    unittest.main(verbosity=2)
