# Diccionario de datos

Describe los campos de las fuentes, de los archivos generados y de las tablas del modelo. Las medidas DAX y sus definiciones están en [modelo-datos.md](modelo-datos.md), y las fórmulas de los indicadores, en [metodologia.md](metodologia.md).

## Fuentes originales (`data/raw/`)

### `estaciones_saludables.csv` y `estaciones_saludables.geo.json`

Una fila por estación (25). Fuente: BA Data. Los dos archivos traen los mismos atributos; el GeoJSON agrega el punto como geometría. Las pruebas automatizadas verifican que coincidan.

| Campo | Tipo | Descripción | Observaciones |
|---|---|---|---|
| `id` | Entero | Identificador de la estación | Único. No es correlativo: va de 3 a 36 |
| `nombre` | Texto | Nombre de la estación | Único |
| `tipo` | Texto | `Fija` o `Móvil` | Sin nulos |
| `estructura` | Texto | `Estructura Grande`, `Estructura Mediana`, `Carpa` o `Sin Información` | Dos estaciones figuran sin información |
| `servicio` | Texto | Lista de servicios separados por ` - ` | Vacío en una estación. Cortado en 254 bytes en dos |
| `direccion` | Texto | Dirección o cruce de calles | |
| `barrio` | Texto | Barrio declarado | |
| `comuna` | Texto | `Comuna N` | Coincide con el polígono en las 25 estaciones |
| `geometry` | Texto (solo en el CSV) | Punto en formato WKT: `POINT (longitud latitud)` | Igual a las coordenadas del GeoJSON |
| Geometría (solo en el GeoJSON) | Punto | Longitud y latitud en grados, CRS84 (WGS84) | Las 25 caen dentro de la ciudad |

### `comunas.geojson`

Un polígono por comuna (15). Fuente: BA Data. Coordenadas en CRS84.

| Campo | Tipo | Descripción | Unidad |
|---|---|---|---|
| `id` | Entero | Identificador del polígono | |
| `objeto` | Texto | Siempre `COMUNA` | |
| `comuna` | Entero | Número de comuna, de 1 a 15 | |
| `barrios` | Texto | Barrios de la comuna, separados por coma | |
| `perimetro` | Decimal | Perímetro del polígono | Metros |
| `area` | Decimal | Superficie del polígono | Metros cuadrados |

### Cuadros del INDEC (Censo 2022)

| Archivo | Campos usados | Unidad |
|---|---|---|
| `c2022_caba_est_c2_1.xlsx`, Cuadro 2.1 | Comuna, superficie y población total | km² y personas |
| `c2022_caba_est_c5_1.xlsx`, Cuadros 5.1.1 a 5.1.15 | Población por grupo de edad de cada comuna | Personas |
| `c2022_caba_est_c7_1.xlsx` y `c2022_caba_est_c8_1.xlsx` | Porcentaje de 65 años y más, e índice de envejecimiento | Solo para contraste |
| `PB2_22nb.xls` (IDECBA) | Población y superficie por comuna | Solo para contraste |

## Archivos generados (`data/processed/`)

### `acceso_comunas_exploratorio.csv`

Una fila por comuna (15). Lo escribe `scripts/analisis_acceso.py`. Los decimales usan punto y se redondean a cuatro cifras.

| Campo | Descripción | Unidad | Origen |
|---|---|---|---|
| `comuna` | Número de comuna | | Polígonos |
| `poblacion` | Población total | Personas | Cuadro 2.1 |
| `superficie_km2` | Superficie oficial | km² | Cuadro 2.1 |
| `poblacion_65_mas` | Población de 65 años y más | Personas | Cuadro 5.1 |
| `estaciones`, `fijas`, `moviles` | Estaciones ubicadas en la comuna, total y por tipo | Estaciones | Estaciones |
| `estaciones_100k` | Estaciones ÷ población × 100.000 | Estaciones cada 100.000 habitantes | Calculado |
| `habitantes_por_estacion` | Población ÷ estaciones | Personas por estación | Calculado |
| `estaciones_km2` | Estaciones ÷ superficie oficial | Estaciones por km² | Calculado |
| `relaciones_servicio` | Suma de los servicios de cada estación de la comuna | Pares estación-servicio | Calculado |
| `servicios_100k` | Relaciones ÷ población × 100.000 | Relaciones cada 100.000 habitantes | Calculado |
| `diversidad` | Servicios distintos de la comuna ÷ 15 | Proporción de 0 a 1 | Calculado |
| `centroide_latitud`, `centroide_longitud` | Centro del polígono, o un punto interior si el centro cae afuera | Grados, CRS84 | Polígonos |
| `cobertura_500m`, `cobertura_1000m`, `cobertura_2000m` | Parte de la superficie a esa distancia o menos de una estación de cualquier comuna | Proporción de 0 a 1 | Grilla de 50 metros |
| `distancia_media_m` | Distancia media a la estación más cercana | Metros, en línea recta | Grilla de 50 metros |
| `cobertura_1000m_presion` | Igual que la cobertura, solo con estaciones que ofrecen Control de Presión Arterial | Proporción de 0 a 1 | Grilla de 50 metros |
| `cobertura_2000m_glucemia` | Igual, solo con estaciones que ofrecen Control de Glucemia | Proporción de 0 a 1 | Grilla de 50 metros |

### `sensibilidad_disponibilidad_relativa.csv`

Una fila por variante del indicador. Lo escribe `scripts/sensibilidad_disponibilidad_relativa.py`.

| Campo | Descripción |
|---|---|
| `escenario` | Variante probada: pesos, componente excluido, normalización o supuesto de truncamiento |
| `spearman`, `kendall` | Correlación del ordenamiento de la variante con el original |
| `mayor_cambio_posicion` | Mayor cantidad de puestos que se mueve una comuna |
| `comunas_cambian_tercio` | Comunas que cambian de grupo respecto del original |
| `posicion_comuna_1` a `posicion_comuna_15` | Puesto de cada comuna en la variante. En las dos últimas filas, porcentaje de sorteos de pesos en que la comuna queda en las cinco últimas o en las cinco primeras |

## Tablas del modelo de Power BI

### `Dim_Estacion`

Una fila por estación. Clave: `id_estacion`.

| Columna | Tipo | Descripción | Procedencia |
|---|---|---|---|
| `id_estacion` | Entero | Clave de la estación | `id` de la fuente |
| `nombre`, `tipo`, `estructura`, `direccion`, `barrio` | Texto | Atributos de la estación, sin espacios sobrantes | Fuente |
| `comuna` | Texto | `Comuna N`. Oculta | Fuente |
| `numero_comuna` | Entero | Número de comuna. Clave hacia `Dim_Comuna` | Derivada de `comuna` |
| `latitud`, `longitud` | Decimal | Coordenadas en grados, CRS84 | GeoJSON, unidas por `id` |
| `cantidad_servicios` | Entero | Servicios válidos registrados. Vacío si la fuente no informa servicios | Calculada en Power Query |
| `flag_calidad` | Texto | `OK`, `SERVICIO_NULL` o `POSIBLE_TRUNCAMIENTO` | Calculada en Power Query |

### `Dim_Servicio`

Una fila por servicio distinto (15). Clave: `id_servicio`.

| Columna | Tipo | Descripción |
|---|---|---|
| `id_servicio` | Entero | Clave, asignada por orden alfabético |
| `servicio` | Texto | Nombre del servicio tal como figura en la fuente |
| `categoria_servicio` | Texto | Sin asignar: no hay un criterio de clasificación documentado |

### `Bridge_Estacion_Servicio`

Una fila por cada servicio que ofrece una estación (191). Oculta. Sin duplicados.

| Columna | Tipo | Descripción |
|---|---|---|
| `id_estacion` | Entero | Clave hacia `Dim_Estacion` |
| `id_servicio` | Entero | Clave hacia `Dim_Servicio` |
| `servicio` | Texto | Nombre del servicio, para control |

### `Dim_Comuna`

Una fila por comuna (15). Clave: `id_comuna`.

| Columna | Tipo | Descripción | Unidad | Procedencia |
|---|---|---|---|---|
| `id_comuna` | Entero | Número de comuna | | Cuadro 2.1 |
| `comuna`, `comuna_corta` | Texto | `Comuna N` y `CN` | | Derivadas |
| `poblacion` | Entero | Población total. Incluye personas en situación de calle | Personas | Cuadro 2.1 |
| `superficie_km2` | Decimal | Superficie oficial | km² | Cuadro 2.1 |
| `densidad_poblacional` | Decimal | Población ÷ superficie oficial | Habitantes por km² | Calculada |
| `poblacion_adulta_mayor` | Entero | Población de 65 años y más | Personas | Cuadro 5.1 |
| `poblacion_censada_edad` | Entero | Total de la hoja de edad. Excluye personas en situación de calle | Personas | Cuadro 5.1 |
| `superficie_poligono_km2` | Decimal | Superficie del polígono | km² | `comunas.geojson` |
| `barrios` | Texto | Barrios de la comuna | | `comunas.geojson` |
| `anio_referencia_poblacion` | Entero | 2022 | Año | Constante |
| `cobertura_500m`, `cobertura_1000m`, `cobertura_2000m` | Decimal | Cobertura de superficie por radio | Proporción de 0 a 1 | Archivo generado |
| `distancia_media_m` | Decimal | Distancia media a la estación más cercana | Metros | Archivo generado |
| `cobertura_1000m_presion_arterial`, `cobertura_2000m_glucemia` | Decimal | Cobertura por radio de un servicio | Proporción de 0 a 1 | Archivo generado |
| `centroide_latitud`, `centroide_longitud` | Decimal | Punto para ubicar la comuna en el mapa | Grados, CRS84 | Archivo generado |

## Relaciones y claves

| Desde (muchos) | Hacia (uno) | Columnas |
|---|---|---|
| `Dim_Estacion` | `Dim_Comuna` | `numero_comuna` y `id_comuna` |
| `Bridge_Estacion_Servicio` | `Dim_Estacion` | `id_estacion` |
| `Bridge_Estacion_Servicio` | `Dim_Servicio` | `id_servicio` |

Las tres relaciones filtran en un solo sentido. No hay filas huérfanas: las medidas de la carpeta `06 - QA` lo controlan y dan cero.
