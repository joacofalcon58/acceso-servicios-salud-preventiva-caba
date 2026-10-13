# Fuentes de datos

Todos los archivos están en `data/raw/`. Esa carpeta reúne las fuentes originales, sin modificar. El md del proyecto proponía `data/external/` para las fuentes externas. Se unificaron en `data/raw/` por indicación del autor.

Fecha de consulta de todas las fuentes: 5 de octubre de 2026.

## Estaciones Saludables

| Atributo | Detalle |
|---|---|
| Archivos | `estaciones_saludables.csv` y `estaciones_saludables.geo.json` |
| Fuente | Vicejefatura de Gobierno, Dirección General de Desarrollo Saludable. Gobierno de la Ciudad Autónoma de Buenos Aires |
| URL | https://data.buenosaires.gob.ar/dataset/estaciones-saludables |
| Fecha de descarga | 29 de septiembre de 2026 |
| Última actualización informada por el portal | 2 de octubre de 2026 |
| Frecuencia de actualización | Trimestral |
| Año de referencia | 2026 |
| Nivel geográfico | Punto, una fila por estación |
| Licencia | CC-BY-2.5-AR |
| Metodología | El portal no publica diccionario de campos |

El 5 de octubre de 2026 el CSV publicado contenía las mismas 25 estaciones que los archivos locales.

El 13 de octubre de 2026 se volvió a verificar: el archivo publicado en `https://cdn.buenosaires.gob.ar/datosabiertos/datasets/vicejefatura-de-gobierno/estaciones-saludables/estaciones_saludables.csv` es idéntico, byte por byte, a `data/raw/estaciones_saludables.csv` (8.446 bytes, 25 filas). El catálogo del portal informa el 2 de octubre de 2026 como fecha de la última modificación del conjunto de datos.

## Polígonos de comunas

| Atributo | Detalle |
|---|---|
| Archivo | `comunas.geojson` |
| Fuente | Jefatura de Gabinete de Ministros, Secretaría de Innovación y Transformación Digital, Gerencia Operativa de Explotación de Datos Geoespaciales |
| URL | https://data.buenosaires.gob.ar/dataset/comunas |
| Descarga | https://cdn.buenosaires.gob.ar/datosabiertos/datasets/innovacion-transformacion-digital/comunas/comunas.geojson |
| Última actualización informada por el portal | 29 de julio de 2026 |
| Frecuencia de actualización | Trimestral |
| Nivel geográfico | Comuna, 15 polígonos |
| Sistema de coordenadas | CRS84 (longitud, latitud) |
| Licencia | CC-BY-2.5-AR |
| Campos | `id`, `objeto`, `comuna`, `barrios`, `perimetro` (metros), `area` (metros cuadrados) |

La superficie que calculan los polígonos suma 204,4 km². Difiere de la superficie oficial del censo (ver más abajo).

## Población, superficie y densidad por comuna

| Atributo | Detalle |
|---|---|
| Archivo principal | `c2022_caba_est_c2_1.xlsx`, Cuadro 2.1 |
| Archivo de contraste | `PB2_22nb.xls`, con las mismas cifras de 2022 y las de 2010 |
| Fuente del archivo principal | INDEC, Censo Nacional de Población, Hogares y Viviendas 2022, resultados definitivos, noviembre de 2023 |
| Fuente del archivo de contraste | Instituto de Estadística y Censos de la Ciudad (IDECBA) sobre la base del Censo 2022 |
| URL principal | https://censo.gob.ar/index.php/datos_definitivos_caba/ |
| URL de contraste | https://www.estadisticaciudad.gob.ar/eyc/banco-datos/poblacion-total-por-sexo-registrado-al-nacer-superficie-y-densidad-poblacional-segun-comuna-ciudad-de-buenos-aires-anos-2010-2022/ |
| Año de referencia | 2022 |
| Nivel geográfico | Comuna |
| Metodología de la población | Población total del censo, incluye personas en situación de calle. Total de la ciudad: 3.121.707 |
| Metodología de la superficie | Valores del documento "Determinación de la superficie correspondiente al Territorio Continental, Antártico e Insular de la República Argentina" del Instituto Geográfico Nacional. Total de la ciudad: 205,9 km² |

Las dos fuentes oficiales coinciden en las 15 comunas para población y superficie.

## Población por edad según comuna

| Atributo | Detalle |
|---|---|
| Archivo | `c2022_caba_est_c5_1.xlsx`, Cuadro 5.1, con una hoja por comuna (5.1.1 a 5.1.15) |
| Fuente | INDEC, Censo 2022, resultados definitivos, noviembre de 2023 |
| URL | https://censo.gob.ar/index.php/datos_definitivos_caba/ |
| Año de referencia | 2022 |
| Nivel geográfico | Comuna, edad simple y grupos de 5 años |
| Metodología | Población total, población en viviendas particulares y población en viviendas colectivas. **Excluye a las personas en situación de calle**: el total es 3.119.304 y no 3.121.707 |

### Archivos de contraste

| Archivo | Contenido | Uso |
|---|---|---|
| `c2022_caba_est_c7_1.xlsx` | Porcentaje de población de 65 años y más por comuna, censos 1970 a 2022. Base: población en viviendas particulares | Contraste del cálculo propio |
| `c2022_caba_est_c8_1.xlsx` | Índice de envejecimiento por comuna, 2010 y 2022 | Indicador complementario, sin usar por ahora |

Descarga de todos los archivos del INDEC: `https://censo.gob.ar/wp-content/uploads/2023/11/<archivo>`. Licencia: el sitio del INDEC no la declara de forma visible. Se cita la fuente en cada uso.

## Datos derivados

| Atributo | Detalle |
|---|---|
| Archivo | `data/processed/acceso_comunas_exploratorio.csv` |
| Generado por | [analisis_acceso.py](../scripts/analisis_acceso.py), a partir de las estaciones, los polígonos de comunas y los cuadros del INDEC |
| Contenido | Indicadores por comuna: población, estaciones, indicadores normalizados, cobertura por radio, distancia media y centro de la comuna |
| Año de referencia | Población de 2022 y estaciones de 2026 |
| Uso | El modelo lee las columnas de cobertura espacial. Si cambia alguna fuente, hay que volver a ejecutar el script |

El script [sensibilidad_disponibilidad_relativa.py](../scripts/sensibilidad_disponibilidad_relativa.py) genera además `data/processed/sensibilidad_disponibilidad_relativa.csv`, con el ordenamiento de las comunas en cada variante del indicador compuesto. El dashboard web lo usa para informar qué comunas se mantienen en el grupo de menor disponibilidad relativa.

## Decisiones sobre las fuentes

- **Superficie.** Se usa la oficial del censo (205,9 km²) para calcular densidad y estaciones por km², porque es la misma fuente que la población. La superficie de los polígonos (204,4 km²) se conserva como columna aparte. La mayor diferencia es la Comuna 4: 22,7 km² oficiales contra 21,7 km² del polígono.
- **Población.** Se usa el total del Cuadro 2.1 (3.121.707 personas). Para el porcentaje de adultos mayores se usa como base el total del Cuadro 5.1 (3.119.304), que excluye a quienes están en situación de calle.
- **Adultos mayores.** Se define como población de 65 años y más. Se suman los grupos de 65 a 69 hasta 95 a 99, más el grupo de 100 y más.
- **Años distintos.** Las estaciones son de 2026 y la población, de 2022. Los datos no se ajustan ni se proyectan.

## Fuentes identificadas, sin evaluar

- **Visitas a Estaciones Saludables.** Dirección General de Estadística y Censos. https://data.buenosaires.gob.ar/dataset/visitas-estaciones-saludables. Publica visitas y concurrencia por comuna. Podría aportar información de demanda. Falta revisar los años que cubre y su nivel de detalle.
- **Proyecciones de población por grupo de edad y comuna, 2010 a 2025.** IDECBA. Permitiría acercar la población al año de las estaciones, pero es una proyección y no un dato censal.
