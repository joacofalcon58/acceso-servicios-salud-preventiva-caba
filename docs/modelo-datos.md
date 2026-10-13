# Modelo de datos

## Esquema

```text
Dim_Comuna (1) ────< Dim_Estacion (1) ────< Bridge_Estacion_Servicio >──── (1) Dim_Servicio
  id_comuna          numero_comuna  id_estacion   id_estacion  id_servicio       id_servicio
```

| Tabla | Grano | Filas | Clave |
|---|---|---|---|
| `Dim_Comuna` | Una fila por comuna | 15 | `id_comuna` |
| `Dim_Estacion` | Una fila por estación | 25 | `id_estacion` |
| `Dim_Servicio` | Una fila por servicio distinto | 15 | `id_servicio` |
| `Bridge_Estacion_Servicio` | Una estación que ofrece un servicio | 191 | `id_estacion` + `id_servicio` |
| `_Medidas` | Contenedor de medidas, sin datos | 1 | No aplica |

## Relaciones

| Desde (muchos) | Hacia (uno) | Dirección del filtro | Activa |
|---|---|---|---|
| `Bridge_Estacion_Servicio[id_estacion]` | `Dim_Estacion[id_estacion]` | Simple, de la dimensión hacia la tabla puente | Sí |
| `Bridge_Estacion_Servicio[id_servicio]` | `Dim_Servicio[id_servicio]` | Simple, de la dimensión hacia la tabla puente | Sí |
| `Dim_Estacion[numero_comuna]` | `Dim_Comuna[id_comuna]` | Simple, de la comuna hacia las estaciones | Sí |

No hay relaciones bidireccionales. El filtro de una comuna llega a las estaciones y, a través de ellas, a la tabla puente. Los filtros de estaciones y de servicios no llegan a `Dim_Comuna`: la población de una comuna no cambia cuando se filtra por tipo de estación o por servicio.

## Decisión: el filtro por servicio no llega a `Dim_Estacion`

Con filtro simple, elegir un servicio filtra la tabla puente pero no las estaciones. Se comprobó en el modelo: con el servicio "Control de Glucemia" seleccionado, `Dim_Estacion` sigue mostrando 25 estaciones y la tabla puente muestra 2.

Consecuencia para el diseño:

- Las medidas que cuentan estaciones y deban responder al filtro de servicio se calculan desde la tabla puente (fase 4).
- Una estación sin filas en la tabla puente (Plaza Houssay) queda fuera de esos conteos cuando hay un servicio seleccionado. Es lo esperado: no se puede afirmar que ofrezca ese servicio.
- Se descartó el filtro bidireccional porque genera ambigüedad con `Dim_Comuna`.

## Claves y visibilidad

Ocultas al usuario: `Dim_Estacion[id_estacion]`, `Dim_Estacion[numero_comuna]`, `Dim_Estacion[comuna]`, `Dim_Servicio[id_servicio]`, `Dim_Comuna[id_comuna]` y toda la tabla `Bridge_Estacion_Servicio`.

La comuna que ve el usuario es `Dim_Comuna[comuna]`, que se ordena por `id_comuna` (Comuna 2 antes de Comuna 10). `Dim_Estacion[comuna]` queda oculta para no duplicar el campo en filtros y ejes.

## Carpetas de medidas

La tabla `_Medidas` organiza las medidas en carpetas:

| Carpeta | Contenido |
|---|---|
| 01 - Estaciones | Fase 4 |
| 02 - Servicios | Fase 4 y 5 |
| 03 - Territorio | Fase 4 |
| 04 - Población | Fase 6, cinco medidas |
| 05 - Acceso | Fase 7, veinte medidas |
| 06 - QA | Creada en la fase 3 |

### Medidas descriptivas (fase 4)

| Carpeta | Medida | Qué cuenta |
|---|---|---|
| 01 - Estaciones | Cantidad Estaciones | Estaciones del contexto actual |
| 01 - Estaciones | Cantidad Estaciones Fijas | Estaciones fijas |
| 01 - Estaciones | Cantidad Estaciones Móviles | Estaciones móviles |
| 02 - Servicios | Cantidad Servicios Diferentes | Servicios distintos del contexto |
| 02 - Servicios | Cantidad Relaciones Estación-Servicio | Filas de la tabla puente |
| 02 - Servicios | Promedio Servicios por Estación | Promedio de servicios por estación con dato |
| 03 - Territorio | Cantidad Comunas con Estaciones | Comunas con al menos una estación |
| 03 - Territorio | Cantidad Barrios con Estaciones | Barrios con al menos una estación |
| 03 - Territorio | Total Comunas CABA | Comunas contadas en `Dim_Comuna` sin filtros (15) |
| 03 - Territorio | Comunas con Presencia | Texto "15 / 15" para tarjeta |

Reglas de diseño:

- **Filtro por servicio.** `Cantidad Estaciones` usa la tabla puente solo cuando hay un servicio filtrado. Sin ese filtro cuenta `Dim_Estacion` directamente, y Plaza Houssay se incluye.
- **Tipo de estación.** Las medidas de fijas y móviles usan `KEEPFILTERS`. Si el usuario filtra por un tipo, la medida del otro tipo queda vacía en vez de ignorar el filtro.
- **Servicios por estación y por comuna.** `Cantidad Servicios Diferentes` da los servicios de una estación o de una comuna según la fila donde se use. No hay una segunda medida con el mismo cálculo.
- **Servicio filtrado.** Con un servicio seleccionado, `Cantidad Servicios Diferentes` y `Cantidad Relaciones Estación-Servicio` cuentan solo ese servicio. Esto es el comportamiento esperado de un filtro, no la cartera completa de las estaciones que lo ofrecen.
- **Promedio.** Excluye estaciones sin servicios informados (Plaza Houssay). Incluye las dos estaciones con posible truncamiento, cuyo valor puede estar subestimado. Con un servicio filtrado usa la cartera completa de las estaciones que lo ofrecen.
- **Vacío y cero.** Las medidas de conteo devuelven vacío cuando no hay datos, para que los gráficos no muestren categorías en cero. Solo las medidas QA muestran 0.

### Medidas de disponibilidad y diversidad (fase 5)

| Carpeta | Medida | Qué calcula |
|---|---|---|
| 02 - Servicios | Estaciones con Servicio | Estaciones que ofrecen el servicio del contexto |
| 02 - Servicios | Estaciones con Información de Servicios | Estaciones del contexto con servicios informados. Es el denominador de la cobertura |
| 02 - Servicios | Cobertura Estaciones % | Estaciones con el servicio sobre estaciones con servicios informados |
| 02 - Servicios | Comunas con Servicio | Comunas con al menos una estación que lo ofrece |
| 02 - Servicios | Cobertura Comunas % | Comunas con el servicio sobre 15 |
| 02 - Servicios | Total Servicios Posibles | Servicios del catálogo observado (15) |
| 02 - Servicios | Diversidad Servicios | Servicios diferentes del contexto sobre el catálogo observado |
| 02 - Servicios | Servicio más disponible | Servicio con más estaciones en el contexto |
| 02 - Servicios | Servicio menos disponible | Servicio con menos estaciones en el contexto |
| 03 - Territorio | Cobertura Territorial % | Comunas con estaciones sobre 15 |
| 03 - Territorio | Comunas solo con Estaciones Móviles | Comunas con móviles y sin fijas |

Reglas de diseño:

- **Denominador de la cobertura de estaciones.** Se usan las 24 estaciones con servicios informados, no las 25. No se puede afirmar que Plaza Houssay no ofrezca un servicio. El resultado es un poco más alto que sobre 25: Actividad Física da 95,8 % en lugar de 92,0 %.
- **Celda de comuna.** En una matriz de servicio por comuna, `Cobertura Estaciones %` es el porcentaje de las estaciones de esa comuna que ofrecen el servicio. `Comunas con Servicio` vale 1 o vacío y sirve como indicador de sí o no.
- **Catálogo de servicios.** `Total Servicios Posibles` cuenta los servicios que aparecen en los datos. Un servicio que ninguna estación registre no figura, y la fuente no publica un catálogo oficial. El denominador de `Diversidad Servicios` depende de esa limitación.
- **Servicio más y menos disponible.** Con empates muestran el primer servicio por orden alfabético y la cantidad de empatados, por ejemplo "Asesoría Nutricional y 3 más". La medida de menos disponible ignora los servicios sin ninguna estación en el contexto.
- **Servicios por comuna.** No hay una medida aparte: `Cantidad Servicios Diferentes` y `Diversidad Servicios` dan el valor por comuna cuando se usan en una fila de comuna.
- **Comparar fijas y móviles.** Las mismas medidas se leen con el tipo en filas o en la leyenda, sin medidas duplicadas.

### Dimensión de comunas y medidas de población (fase 6)

`Dim_Comuna` tiene una fila por comuna, con datos del Censo 2022:

| Columna | Contenido | Fuente |
|---|---|---|
| `id_comuna` | Número de comuna, clave | Cuadro 2.1 del INDEC |
| `comuna` | "Comuna 1" a "Comuna 15" | Calculada en Power Query |
| `poblacion` | Población total, incluye personas en situación de calle | Cuadro 2.1 del INDEC |
| `superficie_km2` | Superficie oficial del censo | Cuadro 2.1 del INDEC |
| `densidad_poblacional` | Población sobre superficie oficial | Calculada en Power Query |
| `poblacion_adulta_mayor` | Población de 65 años y más | Cuadro 5.1 del INDEC, hojas por comuna |
| `poblacion_censada_edad` | Base del porcentaje de 65 y más, excluye personas en situación de calle | Cuadro 5.1 del INDEC |
| `superficie_poligono_km2` | Superficie que calculan los polígonos | `comunas.geojson` |
| `barrios` | Barrios de la comuna, sin tildes, como los publica el polígono | `comunas.geojson` |
| `anio_referencia_poblacion` | 2022 | Documentado en [fuentes.md](fuentes.md) |

| Carpeta | Medida | Qué calcula |
|---|---|---|
| 04 - Población | Poblacion | Población de las comunas del contexto |
| 04 - Población | Superficie km2 | Superficie oficial del censo |
| 04 - Población | Densidad Poblacional | Habitantes por kilómetro cuadrado |
| 04 - Población | Poblacion 65 y mas | Población de 65 años y más |
| 04 - Población | % Poblacion 65 y mas | Porcentaje de 65 años y más sobre la base de la tabla por edad |

Reglas de diseño:

- **Estaciones sin comuna.** No hay: las 25 estaciones tienen su comuna en `Dim_Comuna`, y las 15 comunas tienen al menos una estación.
- **Superficie total.** Sumar las 15 comunas da 206,0 km², porque cada valor oficial está redondeado a un decimal. El total oficial publicado es 205,9 km². La densidad total calculada (15.154 habitantes por km²) difiere así de la publicada (15.161).
- **Nombres de medidas.** Las medidas de población no llevan tildes ni el símbolo de kilómetro cuadrado para evitar problemas de codificación en las referencias.
- **Mayores de 65.** Es una definición propia sobre las tablas del INDEC: se suman los grupos de 65 a 69 años hasta 95 a 99, más el grupo de 100 años y más.

### Indicadores de acceso (fase 7)

La metodología y la justificación del indicador compuesto están en [metodologia.md](metodologia.md).

`Dim_Comuna` suma seis columnas de cobertura espacial, calculadas por el script [analisis_acceso.py](../scripts/analisis_acceso.py) y leídas desde `data/processed/acceso_comunas_exploratorio.csv`: cobertura a 500, 1.000 y 2.000 metros, distancia media a la estación más cercana, cobertura a 1.000 metros de una estación con Control de Presión Arterial y cobertura a 2.000 metros de una estación con Control de Glucemia.

| Grupo | Medida | Qué calcula |
|---|---|---|
| Por población y superficie | Estaciones cada 100.000 habitantes | Estaciones sobre población |
| | Estaciones Fijas cada 100.000 habitantes | Igual, solo fijas |
| | Estaciones Móviles cada 100.000 habitantes | Igual, solo móviles |
| | Servicios cada 100.000 habitantes | Relaciones estación-servicio sobre población |
| | Habitantes por Estación | Población sobre estaciones |
| | Estaciones por km2 | Estaciones sobre superficie oficial |
| Cobertura espacial | Cobertura 500 m %, 1000 m % y 2000 m % | Porcentaje de superficie dentro del radio, ponderado por superficie |
| | Distancia Media a Estación | Metros en línea recta, ponderado por superficie |
| | Cobertura 1000 m Presión Arterial % | Radio de 1.000 metros de una estación con ese control |
| | Cobertura 2000 m Glucemia % | Radio de 2.000 metros de una estación con ese control |
| Indicador compuesto | Estaciones cada 100.000 habitantes (red completa) | Componente sin filtros de estaciones ni de servicios |
| | Diversidad Servicios (red completa) | Componente sin filtros de estaciones ni de servicios |
| | Posicion Relativa Cobertura Poblacional | Posición de 0 a 1 entre las 15 comunas |
| | Posicion Relativa Proximidad | Posición de 0 a 1 entre las 15 comunas |
| | Posicion Relativa Diversidad | Posición de 0 a 1 entre las 15 comunas |
| | Disponibilidad Relativa de la Oferta | Promedio de las tres posiciones, de 0 a 100 |
| | Posicion Disponibilidad Relativa | 1 es la mayor disponibilidad relativa |
| | Grupo de Disponibilidad Relativa | Etiqueta por tercios de las 15 comunas |

Reglas de diseño:

- **Filtros.** Las medidas por población y superficie responden a los filtros de tipo, estructura, barrio y servicio. La cobertura espacial y el indicador compuesto no responden: usan siempre toda la red.
- **Quitar filtros sin perder la comuna.** Los componentes "red completa" quitan los filtros de las columnas de estaciones una por una. No se usó la tabla completa: en el modelo, quitar el filtro de toda `Dim_Estacion` también elimina el filtro que llega desde `Dim_Comuna`, y todas las comunas dan el mismo valor.
- **Contexto de una sola comuna.** Las posiciones, el puntaje y el grupo solo dan valor cuando hay una comuna en el contexto. Con varias comunas o con el total quedan vacíos.
- **Comparar contra las 15 comunas.** Las posiciones recorren la tabla `Dim_Comuna` completa, no solo la columna del número. Con la columna sola, un visual que agrupa por el nombre de la comuna deja una única comuna para comparar y todas quedan en la primera posición.
- **Empates.** La posición compara con seis decimales. Sin eso, el redondeo de la máquina separaba como distintas a dos comunas con el mismo puntaje (2 y 12).

### Agregados para el diseño (fase 8)

- `Dim_Comuna[comuna_corta]`: nombre abreviado (C1 a C15), ordenado por `id_comuna`, para los encabezados de la matriz.
- `Dim_Comuna[centroide_latitud]` y `Dim_Comuna[centroide_longitud]`: un punto central de cada comuna, para ubicar su círculo en el mapa. Lo calcula `scripts/analisis_acceso.py`.
- `Disponibilidad en Comuna`: 1 si alguna estación del contexto ofrece el servicio y 0 si ninguna. Su formato de número lo muestra como círculo lleno o vacío.
- `Color Disponibilidad`: color del símbolo de la matriz, según la disponibilidad.

### Medidas de la carpeta 06 - QA

| Medida | Valor esperado | Valor obtenido |
|---|---|---|
| QA Estaciones sin servicios informados | 1 | 1 |
| QA Estaciones con posible truncamiento | 2 | 2 |
| QA Relaciones huérfanas estación | 0 | 0 |
| QA Relaciones huérfanas servicio | 0 | 0 |
| QA Estaciones sin coordenadas | 0 | 0 |

Las medidas de conteo suman `+ 0` para mostrar 0 en lugar de vacío.

## Preparado para extender

Las dimensiones nuevas (centros de salud, hospitales, vacunatorios) se conectan a `Dim_Comuna` por el número de comuna, con filtro simple de la comuna hacia la dimensión nueva.
