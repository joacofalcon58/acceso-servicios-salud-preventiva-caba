# Acceso a Servicios de Salud Preventiva en CABA

Este proyecto analiza la accesibilidad territorial a servicios de prevención y promoción de la salud en la Ciudad Autónoma de Buenos Aires.

Se integran datos geoespaciales de Estaciones Saludables con información sobre servicios, infraestructura y características territoriales para detectar diferencias en la disponibilidad de prestaciones entre comunas.

El objetivo no es únicamente identificar dónde existen establecimientos, sino analizar si su distribución y su cartera de servicios ofrecen una cobertura territorial homogénea respecto de la población.

![Portada del dashboard](images/portada.png)

**[→ View Live Dashboard](https://joacofalcon58.github.io/acceso-servicios-salud-preventiva-caba/)** · **[→ Explore Source Code](powerbi/)**

## Objetivo

Responder una pregunta: ¿la población de CABA tiene un acceso territorialmente equitativo a los servicios preventivos de las Estaciones Saludables?

La presencia de una estación se trata como una dimensión del acceso, no como evidencia suficiente de cobertura sanitaria.

## Preguntas de negocio

1. ¿Dónde están las estaciones?
2. ¿Qué servicios ofrecen?
3. ¿Existen comunas con poca oferta?
4. ¿Qué servicios tienen menor cobertura territorial?
5. ¿Las estaciones móviles compensan brechas territoriales?
6. ¿Las estaciones fijas ofrecen una cartera de servicios más amplia?
7. ¿Qué comunas tienen menos estaciones respecto de su población?
8. ¿Dónde existe presencia territorial pero baja disponibilidad de prestaciones?
9. ¿Qué territorios conviene analizar primero?

## Fuentes

| Dato | Fuente | Año |
|---|---|---|
| Estaciones Saludables | [BA Data, Gobierno de la Ciudad](https://data.buenosaires.gob.ar/dataset/estaciones-saludables) | 2026 |
| Polígonos de comunas | [BA Data, Gobierno de la Ciudad](https://data.buenosaires.gob.ar/dataset/comunas) | 2026 |
| Población, superficie y población por edad | [INDEC, Censo 2022, resultados definitivos](https://censo.gob.ar/index.php/datos_definitivos_caba/) | 2022 |

El detalle de cada archivo, su fecha de consulta y sus decisiones está en [docs/fuentes.md](docs/fuentes.md).

## Metodología

El proyecto se desarrolló por etapas, con validación al final de cada una:

1. Auditoría de las fuentes.
2. Limpieza y normalización en Power Query.
3. Modelo dimensional.
4. Métricas descriptivas.
5. Análisis de servicios.
6. Incorporación de población y geografía.
7. Indicadores de acceso.
8. Diseño del dashboard.
9. Control de calidad técnico.
10. Hallazgos y documentación.

Los indicadores de acceso incluyen estaciones cada 100.000 habitantes, cobertura espacial por radio y un indicador compuesto de disponibilidad relativa. La justificación de cada decisión, incluida la sensibilidad del indicador compuesto a los pesos, está en [docs/metodologia.md](docs/metodologia.md).

## Modelo de datos

```text
Dim_Comuna (1) ────< Dim_Estacion (1) ────< Bridge_Estacion_Servicio >──── (1) Dim_Servicio
```

| Tabla | Contenido |
|---|---|
| `Dim_Comuna` | 15 comunas, con población, superficie, población de 65 años y más y cobertura espacial |
| `Dim_Estacion` | 25 estaciones, con tipo, estructura, ubicación y calidad del dato |
| `Dim_Servicio` | 15 servicios distintos |
| `Bridge_Estacion_Servicio` | 191 relaciones entre estaciones y servicios |

Las relaciones tienen filtro simple. No hay relaciones bidireccionales. Más detalle en [docs/modelo-datos.md](docs/modelo-datos.md).

## Indicadores principales

| Indicador | Valor en la ciudad |
|---|---|
| Estaciones | 25 (17 fijas y 8 móviles) |
| Comunas con presencia | 15 de 15 |
| Servicios diferentes | 15 |
| Promedio de servicios por estación | 8,0 (fijas 10,0 y móviles 3,9) |
| Estaciones cada 100.000 habitantes | 0,80 |
| Superficie a menos de 1.000 metros de una estación | 35,7 % |

## Dashboard

El dashboard tiene tres páginas.

| Página | Qué muestra |
|---|---|
| Acceso Territorial | Mapa de las estaciones, con filtros por comuna, barrio, tipo, estructura y servicio |
| Disponibilidad de Servicios | Matriz de servicio por comuna, cobertura territorial por servicio y comparación de fijas y móviles |
| Brechas de Acceso | Mapa de comunas por disponibilidad relativa, dispersión de población y estaciones, y tabla de indicadores |

Las decisiones de diseño están en [docs/diseno-dashboard.md](docs/diseno-dashboard.md).

### Versión en HTML

[`index.html`](index.html) ([ver en línea](https://joacofalcon58.github.io/acceso-servicios-salud-preventiva-caba/)) reúne la información de las tres páginas en un único archivo que se abre en cualquier navegador, sin Power BI. Incluye la portada, filtros por comuna, barrio, tipo, estructura y servicio, la matriz de servicios, un mapa de comunas coloreado por Acceso Relativo y un panel de preguntas rápidas. Se genera con `scripts/construir_dashboard_html.py` a partir de los mismos archivos de origen, y sus totales coinciden con las medidas del modelo.

Se puede ver en línea en [joacofalcon58.github.io/acceso-servicios-salud-preventiva-caba/](https://joacofalcon58.github.io/acceso-servicios-salud-preventiva-caba/), publicado con GitHub Pages desde la rama `main`.

## Principales hallazgos

- Las 15 comunas tienen al menos una estación, pero siete dependen de una sola y tres no tienen ninguna estación fija.
- Las cinco comunas con mayor disponibilidad relativa y las cinco con menor disponibilidad tienen una población casi igual (cerca de un millón de habitantes cada grupo). El primer grupo cuenta con 10 estaciones y el segundo, con 5.
- La oferta por habitante varía más de tres veces: de 0,44 a 1,48 estaciones cada 100.000 habitantes.
- Los controles básicos llegan a 13 de las 15 comunas. El Control de Glucemia llega a 2.
- Las estaciones fijas ofrecen en promedio 10,0 servicios y las móviles, 3,9. Las móviles amplían la presencia, pero no la cartera de servicios.

El detalle, con la evidencia y las limitaciones de cada hallazgo, está en [docs/hallazgos.md](docs/hallazgos.md).

## Limitaciones

- No hay información de demanda, de personas atendidas, de capacidad, de horarios ni de dotación profesional.
- Presencia física no equivale a utilización, y disponibilidad declarada no equivale a capacidad efectiva.
- Una estación móvil no necesariamente tiene la misma disponibilidad que una fija.
- La distancia es en línea recta y no representa el tiempo real de viaje.
- La población es del Censo 2022 y las estaciones son de 2026.
- Dos estaciones tienen el campo de servicios posiblemente truncado en la fuente, y una no informa servicios. Los problemas de calidad de los datos están documentados en [docs/qa.md](docs/qa.md).

## Stack tecnológico

Power BI, Power Query, DAX, PBIP, TMDL, PBIR, ArcGIS Maps for Power BI, Git, GitHub, GeoJSON, HTML, CSS y JavaScript (sin librerías) para el dashboard web, y Python (cobertura espacial, validación geográfica y generación del HTML).

## Estructura del repositorio

```text
├── README.md
├── index.html        Dashboard web con la misma información que el informe
├── LICENSE
├── .gitignore
├── data/
│   ├── raw/          Fuentes originales, sin modificar
│   └── processed/    Indicadores por comuna generados por el script
├── powerbi/          Proyecto de Power BI (PBIP)
├── docs/             Metodología, fuentes, modelo, calidad, diseño y hallazgos
├── images/           Capturas del dashboard
└── scripts/          Cobertura espacial, validación geográfica y generación del HTML
```

## Cómo reproducirlo

1. Clonar el repositorio.
2. Abrir `powerbi/acceso-servicios-salud-caba.pbip` en Power BI Desktop.
3. Cambiar el parámetro `RutaProyecto` por la carpeta local del repositorio (Transformar datos, Administrar parámetros).
4. Actualizar los datos.

Para regenerar los indicadores de cobertura espacial y el dashboard en HTML:

```bash
pip install -r scripts/requirements.txt
python scripts/analisis_acceso.py
python scripts/construir_dashboard_html.py
```

El mapa del informe usa ArcGIS Maps for Power BI, que necesita conexión a internet. El dashboard en HTML funciona sin conexión, salvo por la tipografía.

## Licencias

El código y la documentación de este repositorio se publican bajo la licencia MIT.

Los datos de las Estaciones Saludables y de los polígonos de comunas pertenecen al Gobierno de la Ciudad Autónoma de Buenos Aires y están bajo la licencia CC-BY-2.5-AR. Los datos del Censo 2022 pertenecen al INDEC. Se debe citar la fuente al reutilizarlos.

---

AI-assisted development was used for selected documentation, QA and development
workflows. All analytical logic, results and final implementation were reviewed
and validated manually.
