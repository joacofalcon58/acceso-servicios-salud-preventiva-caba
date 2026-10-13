# Informe de calidad de datos (QA)

## Fase 1: auditoría de fuentes

Fecha de la auditoría: 5 de octubre de 2026.

Archivos auditados, sin modificar:

- `data/raw/estaciones_saludables.csv`
- `data/raw/estaciones_saludables.geo.json`

### Resumen

| Control | Resultado |
|---|---|
| Registros CSV | 25 |
| Registros GeoJSON | 25 |
| IDs coincidentes | 25 |
| IDs faltantes | 0 en ambos sentidos |
| Duplicados por `id` | 0 |
| Duplicados por nombre, dirección o coordenadas | 0 |
| Diferencias de atributos entre CSV y GeoJSON | 0 |
| Diferencia máxima de coordenadas entre CSV (WKT) y GeoJSON | Menor a 1e-13 grados |
| Coordenadas fuera de rango | 0 |
| Errores de codificación | 0 |

Los dos archivos representan el mismo universo. El modelo usará una sola tabla de estaciones.

### Universo verificado

Los valores se recalcularon desde los archivos.

| Dimensión | Detalle |
|---|---|
| Tipo | 17 fijas, 8 móviles |
| Estructura | 12 estructuras grandes, 4 estructuras medianas, 7 carpas, 2 sin información |
| Comunas | 15 de 15 |
| Barrios | 21 |
| IDs | Entre 3 y 36, no consecutivos |

Cruce de tipo y estructura:

| Tipo | Estructura | Estaciones |
|---|---|---|
| Fija | Estructura Grande | 12 |
| Fija | Estructura Mediana | 4 |
| Fija | Carpa | 1 |
| Móvil | Carpa | 6 |
| Móvil | Sin Información | 2 |

### Nulos por campo

| Campo | CSV | GeoJSON |
|---|---|---|
| `id` | 0 | 0 |
| `nombre` | 0 | 0 |
| `tipo` | 0 | 0 |
| `estructura` | 0 | 0 |
| `servicio` | 1 | 1 |
| `direccion` | 0 | 0 |
| `barrio` | 0 | 0 |
| `comuna` | 0 | 0 |
| `geometry` | 0 | 0 |

El valor "Sin Información" de `estructura` (2 estaciones móviles) no es un nulo técnico, pero equivale a un dato faltante.

### Formato y codificación

- El CSV está en UTF-8 con BOM. Power Query debe leerlo con codificación 65001.
- No hay caracteres corruptos ni espacios sobrantes en ningún campo.
- El campo `comuna` respeta el formato "Comuna N" en los 25 registros.
- El GeoJSON declara el sistema de referencia CRS84: el orden es longitud, latitud.

### Coordenadas

| Eje | Mínimo | Máximo |
|---|---|---|
| Latitud | -34,6903 | -34,5518 |
| Longitud | -58,4931 | -58,3696 |

Los 25 puntos caen dentro del rectángulo que contiene a la Ciudad Autónoma de Buenos Aires (CABA).

**Limitación.** Esta validación usa un rectángulo, no el límite real de la ciudad. La validación punto en polígono, y la verificación de que cada estación cae en la comuna declarada, quedan para la fase 6, cuando se incorporen los polígonos de comunas.

### Servicios

Al separar el campo `servicio` por el delimitador " - " se obtienen 192 elementos y 16 textos distintos: 15 servicios y 1 fragmento truncado. Las relaciones estación-servicio válidas son 191.

| Servicio | Estaciones |
|---|---|
| Actividad Física | 23 |
| Asesoría Nutricional | 19 |
| Control de Peso | 19 |
| Control de Presión Arterial | 19 |
| Control de Talla | 19 |
| Servicios de Enfermería | 18 |
| Taller Cognitivo | 15 |
| Talleres Literarios | 15 |
| Cumpleaños Saludables | 15 |
| Talleres de Escritura | 15 |
| Talleres para Ejercitar tu Mente | 8 |
| Control de Glucemia | 2 |
| Actividades para Adultos Mayores | 2 |
| Actividades para Niños (Juegotecas) | 1 |
| Casilleros y Cambiadores | 1 |
| Actividade (fragmento truncado) | 1 |

- Ningún servicio se repite dentro de una misma estación.
- No hay variantes de escritura del mismo servicio (mayúsculas, tildes o espacios).
- "Taller Cognitivo" y "Talleres para Ejercitar tu Mente" aparecen como servicios distintos. El primero solo figura en estaciones fijas y el segundo solo en móviles. No se unifican sin una definición oficial.

Cantidad de servicios por estación, según el tipo:

| Tipo | Estaciones | Servicios por estación | Promedio |
|---|---|---|---|
| Fija | 17 | Entre 9 y 11, y 1 estación sin dato | 10,0 sobre las 16 con dato |
| Móvil | 8 | 7 en 3 estaciones y 2 en 5 estaciones | 3,9 |

Los valores de las fijas excluyen el fragmento truncado de Parque Los Andes: la estación suma 10 servicios válidos. Plaza Almagro es la única con 11.

## Problemas detectados

### P1. Plaza Houssay sin servicios informados

- **Registro:** id 36, Estación Saludable Plaza Houssay (fija, Comuna 2).
- **Evidencia:** `servicio` vacío en CSV y `null` en GeoJSON.
- **Tratamiento:** no se asume que la estación no ofrece servicios. Se clasifica como "Información de servicios no disponible", con `Flag_Calidad_Servicio = SERVICIO_NULL`. No genera filas en la tabla puente.
- **Impacto:** los promedios de servicios por estación deben excluirla del denominador o informarla aparte.

### P2. Parque Los Andes con servicio truncado

- **Registro:** id 11, Estación Saludable Parque Los Andes (fija, Comuna 15).
- **Evidencia:** el campo termina en "Actividade" y mide exactamente 254 bytes (250 caracteres). 254 bytes es el largo máximo de un campo de texto en el formato Shapefile, uno de los formatos en que se publica el conjunto de datos.
- **Fuente original:** el CSV publicado en BA Data presenta el mismo corte (consulta del 5 de octubre de 2026). No es posible recuperar el texto completo de forma confiable.
- **Tratamiento:** `Flag_Calidad_Servicio = POSIBLE_TRUNCAMIENTO`. El fragmento "Actividade" no se completa y no genera fila en la tabla puente. Los 10 servicios completos sí se cargan.
- **Impacto:** la estación puede ofrecer más servicios que los registrados. Es la única estación con datos que no registra "Actividad Física", lo que puede ser consecuencia del corte.

### P3. Parque Avellaneda en el límite de longitud

- **Registro:** id 8, Estación Saludable Parque Avellaneda (fija, Comuna 9).
- **Evidencia:** el campo mide también exactamente 254 bytes. Termina en un servicio completo ("Control de Talla"), por lo que el corte no es visible.
- **Tratamiento:** `Flag_Calidad_Servicio = POSIBLE_TRUNCAMIENTO`. Los 10 servicios se cargan sin cambios.
- **Impacto:** la lista puede estar incompleta. Este problema no figuraba en el relevamiento inicial del proyecto.

### P4. Nombres de barrio con diferencias respecto de la denominación oficial

- **Evidencia:** "San Cristobal" (sin tilde) y "Villa Del Parque" (preposición con mayúscula). También "Parque De La Ciudad" en el nombre de la estación id 35.
- **Tratamiento:** se documenta. La corrección se hará en Power Query con una tabla de equivalencias explícita, no a mano, cuando se incorpore la lista oficial de barrios.
- **Impacto:** bajo hoy. Puede impedir el cruce con fuentes externas por nombre de barrio.

### P5. Estructura sin información

- **Registros:** 2 estaciones móviles.
- **Tratamiento:** se conserva el valor "Sin Información" como categoría propia.

### P6. El conjunto de datos no incluye días ni horarios

- **Evidencia:** la descripción oficial del conjunto de datos menciona "días y horarios", pero los archivos no traen esos campos.
- **Impacto:** no se puede medir disponibilidad temporal. Se suma a las limitaciones del análisis.

## Valores del campo de calidad

| `Flag_Calidad_Servicio` | Estaciones | IDs |
|---|---|---|
| OK | 22 | Resto |
| SERVICIO_NULL | 1 | 36 |
| POSIBLE_TRUNCAMIENTO | 2 | 8, 11 |

## Conclusión de la fase 1

No hay errores bloqueantes. Los seis problemas quedan documentados y ninguno requiere modificar los archivos originales.

## Fase 2: ETL y normalización

Fecha de la validación: 5 de octubre de 2026.

### Consultas de Power Query

| Consulta | Carga al modelo | Contenido |
|---|---|---|
| `RutaProyecto` | Parámetro | Carpeta raíz del repositorio en el equipo local |
| `LimiteBytesServicio` | Parámetro | 254, largo máximo de un campo de texto en formato Shapefile |
| `00_SRC_Estaciones_CSV` | No | Lectura cruda del CSV |
| `00_SRC_Estaciones_GeoJSON` | No | Lectura del GeoJSON, solo id y coordenadas |
| `01_STG_Estaciones` | No | Estaciones limpias, con número de comuna, coordenadas y flag de calidad |
| `01_STG_EstacionServicio` | No | Relación estación-servicio en formato largo |
| `01_STG_Servicios` | No | Catálogo de servicios con identificador |
| `Dim_Estacion` | Sí | Una fila por estación |
| `Dim_Servicio` | Sí | Una fila por servicio |
| `Bridge_Estacion_Servicio` | Sí | Una fila por estación y servicio |

### Reglas aplicadas

- **Fuente única.** Los atributos se toman del CSV. El GeoJSON aporta solo latitud y longitud, unidas por `id`.
- **Limpieza de texto.** Se quitan espacios sobrantes y caracteres de control. Un texto vacío pasa a nulo. No se cambian mayúsculas ni tildes de los nombres de la fuente.
- **Flag de calidad.** `SERVICIO_NULL` si el campo está vacío. `POSIBLE_TRUNCAMIENTO` si el campo alcanza los 254 bytes. `OK` en el resto. La regla se calcula sobre el dato, no sobre una lista fija de estaciones.
- **Fragmentos truncados.** En una estación con posible truncamiento, el último elemento de la lista se conserva solo si coincide con un servicio confirmado en otra posición o en otra estación. Con esta regla se descarta "Actividade" y se conserva "Control de Talla" de Parque Avellaneda.
- **Cantidad de servicios.** Queda vacía, no en cero, para la estación sin servicios informados.
- **Identificador de servicio.** Se asigna por orden alfabético. Puede cambiar si la fuente incorpora servicios nuevos.
- **Categoría de servicio.** Queda sin asignar hasta definir un criterio documentado.

### Validación del resultado

Las consultas se ejecutaron en Power BI Desktop y el resultado se comparó con el perfilado independiente de la fase 1.

| Control | Esperado | Obtenido |
|---|---|---|
| Filas en `Dim_Estacion` | 25 | 25 |
| `id_estacion` únicos | 25 | 25 |
| Estaciones fijas y móviles | 17 y 8 | 17 y 8 |
| Comunas y barrios | 15 y 21 | 15 y 21 |
| Filas en `Dim_Servicio` | 15 | 15 |
| `id_servicio` únicos | 15 | 15 |
| Filas en `Bridge_Estacion_Servicio` | 191 | 191 |
| Pares estación-servicio únicos | 191 | 191 |
| IDs huérfanos en la tabla puente | 0 | 0 |
| Estaciones sin coordenadas | 0 | 0 |
| Rango de latitud y longitud | Igual al de la fase 1 | Igual |
| Estaciones por flag | 22 OK, 2 posible truncamiento, 1 nulo | Igual |
| Estaciones por servicio | Tabla de la fase 1 | Igual en los 15 servicios |

No hay errores bloqueantes.

## Fase 3: modelo dimensional

Fecha de la validación: 5 de octubre de 2026. Detalle del esquema en [modelo-datos.md](modelo-datos.md).

| Control | Resultado |
|---|---|
| `Dim_Estacion[id_estacion]` único | Sí, 25 de 25 |
| `Dim_Servicio[id_servicio]` único | Sí, 15 de 15 |
| Combinación `id_estacion` + `id_servicio` duplicada en la tabla puente | 0 |
| Cardinalidad de las dos relaciones | Muchos a uno |
| Dirección del filtro | Simple, sin relaciones bidireccionales |
| Filas huérfanas en la tabla puente | 0 |
| Claves técnicas ocultas | Sí |

Hallazgo de diseño: el filtro por servicio no propaga a `Dim_Estacion`. Está documentado en [modelo-datos.md](modelo-datos.md) y se resuelve en las medidas de la fase 4.

No hay errores bloqueantes.

## Fase 4: métricas descriptivas

Fecha de la validación: 5 de octubre de 2026. Medidas documentadas en [modelo-datos.md](modelo-datos.md).

Las medidas se compararon con un cálculo independiente en Python sobre el CSV, en seis escenarios de filtro y en las 15 comunas.

| Escenario | Estaciones | Fijas | Móviles | Comunas | Barrios | Promedio de servicios | Resultado |
|---|---|---|---|---|---|---|---|
| Sin filtro | 25 | 17 | 8 | 15 | 21 | 7,96 | Coincide |
| Servicio = Control de Glucemia | 2 | 2 | 0 | 2 | 2 | 10,5 | Coincide |
| Servicio = Talleres para Ejercitar tu Mente | 8 | 0 | 8 | 6 | 8 | 3,875 | Coincide |
| Tipo = Fija | 17 | 17 | 0 | 12 | 14 | 10,0 | Coincide |
| Tipo = Móvil | 8 | 0 | 8 | 6 | 8 | 3,875 | Coincide |
| Estación = Plaza Houssay | 1 | 1 | 0 | 1 | 1 | Vacío | Coincide |

Por comuna, las 15 filas coinciden en estaciones, fijas, móviles, servicios diferentes, relaciones y promedio.

### Hallazgo corregido durante la validación

La primera versión de las medidas de fijas y móviles ignoraba el filtro de tipo: con "Fija" seleccionado, la tarjeta de móviles mostraba 8. Se corrigió con `KEEPFILTERS` y se verificó que ahora queda vacía.

### Diferencia entre definiciones, no error

Con un servicio filtrado, el cálculo de Python informa la cartera completa de las estaciones que lo ofrecen (por ejemplo 14 servicios para Control de Glucemia), mientras que el modelo informa 1, el servicio filtrado. Se mantiene el comportamiento del modelo porque es el que espera quien usa un filtro.

No hay errores bloqueantes.

## Fase 5: disponibilidad y diversidad de servicios

Fecha de la validación: 5 de octubre de 2026. Medidas documentadas en [modelo-datos.md](modelo-datos.md).

### Validación

- **Matriz servicio por comuna.** Se compararon las 134 celdas con valor (estaciones y porcentaje de cobertura por celda) contra un cálculo independiente en Python sobre el CSV. Diferencias: 0 celdas con distinto valor, 0 sobrantes, 0 faltantes.
- **Por servicio.** Estaciones, comunas, cobertura de comunas y cobertura de estaciones de los 15 servicios coinciden con el cálculo independiente.
- **Por comuna.** Servicios diferentes y diversidad de las 15 comunas coinciden con la fase 4.
- **Por tipo.** Servicio más y menos disponible, servicios diferentes, comunas y promedio de fijas y móviles coinciden con el cálculo independiente.
- **Contextos límite.** Servicio filtrado, comuna 1 y Plaza Houssay devuelven lo esperado, incluido vacío para Plaza Houssay.
- **Todas las medidas.** Las 26 medidas del modelo se evalúan sin error en una misma consulta.

### Hallazgo corregido durante la construcción

Las medidas de servicio más y menos disponible se crearon con una variable llamada `top`, que es una palabra reservada de DAX. La herramienta informó la creación como exitosa, pero la medida quedó en estado de error semántico. Se detectó porque toda consulta que la usaba fallaba. Se renombraron las variables y se confirmó que las 26 medidas evalúan bien.

### Resultados a tener en cuenta

Son resultados del cálculo, no conclusiones. La interpretación está pendiente de la fase 10.

| Resultado | Dato |
|---|---|
| Servicio más disponible | Actividad Física: 23 de 24 estaciones, 14 de 15 comunas |
| Servicios menos disponibles | Actividades para Niños (Juegotecas) y Casilleros y Cambiadores: 1 estación y 1 comuna cada uno |
| Control de Glucemia y Actividades para Adultos Mayores | 2 estaciones y 2 comunas cada uno |
| Comuna sin Actividad Física | Comuna 15, cuya única estación es Parque Los Andes, con el campo de servicios truncado |
| Comunas con 2 servicios | Comunas 1 y 10, que solo tienen una estación móvil |
| Comunas solo con estaciones móviles | Comunas 1, 10 y 13 |
| Comunas con ambos tipos | Comunas 6, 8 y 12 |

Fijas y móviles:

| Indicador | Fijas | Móviles |
|---|---|---|
| Estaciones con servicios informados | 16 de 17 | 8 de 8 |
| Promedio de servicios por estación | 10,0 | 3,9 |
| Servicios diferentes | 14 de 15 | 7 de 15 |
| Diversidad | 93,3 % | 46,7 % |
| Comunas con presencia | 12 de 15 | 6 de 15 |

La ausencia de Actividad Física en la comuna 15 puede deberse al truncamiento de Parque Los Andes (problema P2). Si se confirma, la cobertura de esa actividad sería 100 %. Las dos estaciones truncadas se incluyen con los servicios que se pudieron leer, por lo que las coberturas pueden estar subestimadas.

No hay errores bloqueantes.

## Fase 6: población y geografía

Fecha de la validación: 5 de octubre de 2026. Fuentes y decisiones en [fuentes.md](fuentes.md). Modelo en [modelo-datos.md](modelo-datos.md).

### Validación de las fuentes

| Control | Resultado |
|---|---|
| Población por comuna: INDEC, Cuadro 2.1 contra IDECBA | Coinciden las 15 comunas |
| Suma de la población de las 15 comunas | 3.121.707, igual que el total del censo |
| Suma de las 15 hojas de edad | 3.119.304 personas, igual que el total del Cuadro 5.1. La diferencia con 3.121.707 son las 2.403 personas en situación de calle, que esa tabla excluye |
| Población de 65 años y más, suma de las 15 comunas | 551.010, el 17,7 % de la población, igual que la cifra del censo |
| Porcentaje de 65 y más calculado contra el publicado por el INDEC (Cuadro 7.1) | Coincide en las 15 comunas, con la misma base de población en viviendas particulares |
| Grupos de 5 años contra edades simples | La suma de 65 y más da igual de las dos formas en las 15 comunas |
| Polígonos de comunas | 15, en CRS84, con barrios, perímetro y área |

### Validación de las estaciones contra los polígonos

El script [validar_estaciones_comunas.py](../scripts/validar_estaciones_comunas.py) ubica cada punto en el polígono de comunas, con trazado de rayos. Reemplaza la validación por rectángulo de la fase 1.

| Control | Resultado |
|---|---|
| Estaciones fuera de la Ciudad | 0 |
| Estaciones cuya comuna declarada difiere de la del polígono | 0 |
| Estaciones cuyo barrio no figura entre los barrios de su comuna | 0 |

### Validación del modelo

Valores de `Dim_Comuna` en Power BI Desktop contra el cálculo independiente en Python:

| Control | Resultado |
|---|---|
| Filas y claves únicas | 15 y 15 |
| Población, superficie y densidad | Coinciden con el Cuadro 2.1 en las 15 comunas |
| Población de 65 y más y base de edad | Coinciden en las 15 comunas |
| Estaciones sin comuna en `Dim_Comuna` | 0 |
| Comunas sin estaciones | 0 |
| Total de comunas calculado | 15, ya no es un valor fijo |
| Población con un tipo de estación filtrado | 3.121.707, no cambia |

### Problemas encontrados durante la construcción

- **Delimitador de texto.** `Text.BetweenDelimiters` buscó el punto final desde el comienzo del título y no después de "Comuna ", y devolvió vacío. Se reemplazó por `Text.AfterDelimiter` seguido de `Text.BeforeDelimiter`.
- **Espacio de no separación.** Los títulos del INDEC usan el carácter de espacio de no separación (código 160) entre "Comuna" y el número. Se normalizan antes de buscar.
- **Fallo silencioso.** Los dos errores dejaron a la población de 65 y más vacía sin interrumpir la actualización del modelo. Se detectaron al consultar los valores. Convendría que la actualización falle ante un valor vacío en esta tabla.

### Pendiente para la fase 7

Los indicadores normalizados por población (estaciones cada 100.000 habitantes, habitantes por estación, estaciones por km²) se construyen en la fase 7.

No hay errores bloqueantes.

## Fase 7: indicadores de acceso

Fecha de la validación: 5 de octubre de 2026. Método y decisiones en [metodologia.md](metodologia.md).

### Validación de las medidas

Las medidas de Power BI Desktop se compararon con el cálculo independiente del script [analisis_acceso.py](../scripts/analisis_acceso.py), que usa la población y las estaciones directamente de las fuentes.

| Control | Resultado |
|---|---|
| Estaciones cada 100.000 habitantes, habitantes por estación, estaciones por km² y servicios cada 100.000, en las 15 comunas | Coinciden |
| Cobertura a 500, 1.000 y 2.000 metros, distancia media y cobertura de servicios, en las 15 comunas | Coinciden con el archivo generado |
| Puntaje de Acceso Relativo en las 15 comunas | Coincide con el cálculo del script, con los tres componentes y pesos iguales |
| Posición de las 15 comunas | Coincide con el script |
| Acceso Relativo con un filtro de tipo móvil o de un servicio | No cambia: usa toda la red |
| Posición y grupo con el total de comunas | Vacíos |

Totales de la ciudad: 0,80 estaciones cada 100.000 habitantes (0,54 fijas y 0,26 móviles), 124.868 habitantes por estación, cobertura de la superficie de 9,6 % a 500 metros, 35,7 % a 1.000 y 79,1 % a 2.000, y distancia media de 1.421 metros.

### Problemas encontrados durante la construcción

- **Quitar filtros de toda la tabla de estaciones.** La primera versión de los componentes "red completa" usó `REMOVEFILTERS(Dim_Estacion)`. Eso quitó también el filtro de comuna: las comunas daban el mismo valor, todas quedaban empatadas en 0,5 y el indicador compuesto tenía un tercio de información. Se detectó al comparar con el script. Se reemplazó por la eliminación de los filtros de columna uno por uno.
- **Posición en el total.** La posición y el grupo daban 16 y "Menor disponibilidad relativa" con el total de comunas en el contexto. Se agregó una condición de una sola comuna.
- **Empate roto por redondeo.** Dos comunas con el mismo puntaje quedaban en posiciones distintas. Se compara con seis decimales.

### Lo que no se validó

- La cobertura espacial depende de un cálculo propio con una aproximación de distancias en línea recta. Se verificó que las medidas del modelo lean bien el archivo, pero no se contrastó contra otra herramienta geográfica.
- Los radios de 500, 1.000 y 2.000 metros son exploratorios.

No hay errores bloqueantes.

## Fase 8: diseño de Power BI

Fecha de la validación: 5 de octubre de 2026. Diseño y decisiones en [diseno-dashboard.md](diseno-dashboard.md).

### Validación técnica

| Control | Resultado |
|---|---|
| Visuales, páginas, orden de páginas e informe contra los esquemas oficiales de Microsoft | 47 visuales y 3 páginas sin errores |
| Campos y medidas de los visuales contra el modelo | Las 103 referencias existen |
| Campos repetidos dentro de un mismo visual | Ninguno |
| Configuración de los dos mapas de ArcGIS | El campo del símbolo y los campos de ubicación existen en la capa |
| Matriz de la página 2 | 15 columnas ordenadas de C1 a C15. Símbolo lleno o vacío y color según la disponibilidad |
| Datos del mapa de estaciones | 25 estaciones con todos sus campos |
| Datos del mapa de comunas | 15 comunas con coordenadas, grupo, población y puntaje. Los valores coinciden con el cálculo independiente |
| Texto alternativo | Todos los visuales con datos lo tienen |

### Problemas encontrados durante la construcción

- **Mapas nativos en blanco.** El mapa de estaciones (Azure Maps) y el mapa de formas de comunas se mostraron vacíos en Power BI Desktop. En el primero la causa más probable era haber puesto el nombre de la estación como ubicación, que Azure Maps intenta buscar como dirección. En el segundo no se pudo determinar. Se reemplazaron por ArcGIS Maps for Power BI, con coordenadas.
- **Campos repetidos en el mapa de estaciones.** La estación y el tipo estaban a la vez en la categoría, la leyenda y los tooltips, y Power BI Desktop mostró el error "Repeated indices found in GroupBy or Projections". La revisión contra los esquemas no lo detecta. Se agregó la comprobación de campos repetidos a la revisión de los 47 visuales.
- **Campos mal repartidos al cambiar a ArcGIS.** Al convertir el visual, Desktop repartió los campos en casilleros que no correspondían: el tipo como ubicación, el nombre como color, la estructura como hora. Se reasignaron y se dejó una configuración de símbolos coherente: azul para las fijas, naranja para las móviles, y tres tonos de azul para los grupos de comunas.
- **Mapa de comunas con ubicación por nombre.** ArcGIS buscaba "Comuna 1" como nombre de lugar en todo el mundo, sin garantía de acertar. Se cambió a un punto en el centro de cada comuna, con latitud y longitud propias (columnas nuevas de `Dim_Comuna`). Ya no es un mapa de polígonos coloreados, sino de círculos.
- **Posición relativa mal calculada dentro de los visuales.** Con la comuna como categoría de un visual, las medidas de posición daban 1 para todas las comunas y el Acceso Relativo daba 100 para todas. Mi validación anterior iteraba fila por fila y no reprodujo ese contexto. La causa: `ALL` sobre una sola columna deja activos los filtros de las otras columnas de la tabla. Se reemplazó por `ALL` sobre la tabla completa y se validó con una consulta agrupada por comuna, que es lo que usan los visuales.
- **Tema propio eliminado por Power BI Desktop.** Al guardar, Desktop quitó el archivo del tema que se había escrito a mano y dejó una referencia colgante. Se eliminó la referencia y el formato de fondo, borde y título quedó definido en cada visual. Más tarde se importó el tema "CABA Salud Preventiva" desde Desktop, que sí lo conserva.
- **Color de los símbolos de la matriz.** El gris elegido tenía poco contraste. Se oscureció.

### Colores fuera del tema

Al importar el tema "CABA Salud Preventiva", los visuales siguieron mostrando colores ajenos: el azul y el naranja, los grises de texto y los símbolos de los mapas estaban fijados en cada visual y tenían prioridad sobre el tema. El 13 de octubre de 2026 se reemplazaron por los valores del tema en los 48 visuales, en la medida de color de la matriz y en los símbolos de los dos mapas de ArcGIS.

| Uso | Antes | Ahora |
|---|---|---|
| Estaciones fijas | `#2a78d6` | `#0A5599` |
| Estaciones móviles | `#eb6834` | `#BD7150` |
| Degradado de la dispersión | `#cde2fb` a `#0d366b` | `#86DCE5` a `#0A2A3C` |
| Texto y títulos | `#0b0b0b`, `#52514e`, `#6b6a66` | `#0A2A3C`, `#4A4F55`, `#5F6B6D` |
| Bordes de los visuales | `#E1E3E8` | `#DCEFF4` |

Los únicos colores que quedan en los visuales son los del tema y el blanco de las tarjetas. El amarillo del tema no pasa el verificador de contraste y se descartó para datos. Los colores de fijas y móviles se ajustaron después al manual (ver la sección siguiente).

### Ajuste a los colores del Manual de estilo

Al comparar con el Manual de estilo de la Ciudad se vio que el azul `#0A5599` y la terracota `#BD7150` estaban en el tema, pero no en el manual. El 13 de octubre de 2026 se reemplazaron en los 48 visuales, en los símbolos de los mapas, en la medida de color de la matriz y en el HTML.

| Uso | Antes | Ahora |
|---|---|---|
| Estaciones fijas, barras y matriz | `#0A5599` | `#0A2A3C` |
| Estaciones móviles | `#BD7150` | `#2F8F8A` |
| Fijas en tema oscuro del HTML | `#4B8DDC` | `#86DCE5` |

El verificador de paletas da, para el par `#0A2A3C` y `#2F8F8A`: separación para daltonismo 32,4, visión normal 32,9 y contraste suficiente (aprobados); banda de luminosidad y piso de saturación (no aprobados, por ser un azul casi negro y un verde agua poco saturado). En oscuro, `#86DCE5` con `#2F8F8A`: 24,9 y 25,0, con los mismos dos controles no aprobados. No se pudo ver Power BI renderizado con los colores nuevos.

### Alineación de visuales y tarjeta de servicio menos disponible

- **HTML.** En cada sección las dos columnas terminan a la misma altura (se midió con ancho de escritorio): el mapa y las tres tarjetas de la derecha en la página 1, la matriz y las dos tarjetas de la derecha en la 2, y el mapa y la dispersión en la 3. La dispersión calcula su altura a partir de la tarjeta del mapa y se vuelve a dibujar al cambiar el tamaño de la ventana.
- **Power BI.** La tarjeta "Servicio menos disponible" se ensanchó de 365 a 540 píxeles, con fuente de 16 puntos y ajuste de línea activado, para que el nombre largo ("Actividades para Niños (Juegotecas) y 1 más") no se corte. Las otras tres tarjetas de la página 2 se reacomodaron para que todas sigan alineadas. No se pudo ver Power BI renderizado: falta confirmar que el ajuste de línea funciona en esa tarjeta.

- **HTML, tabla de indicadores.** La tabla "Indicadores por comuna" y la de "Fijas y móviles" ya no necesitan desplazamiento horizontal a 1280, 1440 y 1920 píxeles de ancho: los encabezados pasan a dos líneas, el padding es menor y el grupo se muestra como Mayor, Intermedia o Menor.
- **HTML, aviso de calidad de datos.** Se quitó el recuadro de la página 2. Las limitaciones de las estaciones con servicios truncados o sin informar siguen documentadas en las Fases 1 y 2 de este archivo y en `docs/hallazgos.md`.

### Lo que no se pudo validar

- **El aspecto de las páginas.** No se pudo ver el reporte renderizado, así que no se verificaron solapamientos, cortes de texto ni proporciones.
- **La configuración de ArcGIS.** Los símbolos y la leyenda de los dos mapas se escribieron a mano sobre el formato que guardó Desktop. Si alguno no se ve como se describe, se ajusta desde el panel de formato del visual.
- **El color por Acceso Relativo** en la dispersión y el color de los símbolos de la matriz.

Estas verificaciones visuales quedan para la fase 9.

## Fase 9: control de calidad técnico y visual

Fecha de la validación: 5 de octubre de 2026.

### Modelo

Se ejecutaron 30 comprobaciones en Power BI Desktop. Los resultados son los esperados en las 30, después de corregir un caso (ver más abajo). Tras la corrección se repitió el conjunto principal de comprobaciones.

| Grupo | Comprobaciones | Resultado |
|---|---|---|
| Claves únicas | Estaciones, servicios y comunas. Pares estación-servicio de la tabla puente | Sin duplicados |
| Integridad referencial | Filas huérfanas de la tabla puente. Estaciones sin comuna. Comunas sin estaciones | 0 |
| Texto | Servicios duplicados por diferencias de mayúsculas o espacios | 0 |
| Coordenadas | Estaciones sin coordenadas o fuera del rectángulo de la ciudad | 0 |
| Doble conteo | La suma de estaciones por comuna, tipo, estructura y barrio da el total. Fijas más móviles da el total en cada comuna. Con un servicio filtrado, la suma por comuna da las estaciones que lo ofrecen | Correcto |
| Relaciones | Las relaciones estación-servicio suman 191 por servicio y por estación | Correcto |
| Población | Total de 3.121.707 y 551.010 de 65 años y más. No cambia con los filtros de estaciones ni de servicios | Correcto |
| Indicadores | Estaciones cada 100.000 habitantes consistente con las estaciones. Coberturas entre 0 y 100 %. Acceso Relativo entre 0 y 100. Posiciones entre 1 y 15. Grupos de 5, 5 y 5 | Correcto |
| Calidad de datos | Dos estaciones con posible truncamiento y una sin servicios informados | Correcto |

La cardinalidad, la dirección de los filtros y la ausencia de relaciones bidireccionales están verificadas desde la fase 3.

### Hallazgo: las estaciones sin servicios informados figuraban con 0 servicios

Una comprobación falló: el promedio de servicios por estación daba 7,64 en lugar de 7,96. Se encontró que el paso de Power Query de `Dim_Estacion` reemplazaba los valores vacíos de la cantidad de servicios por 0. Con ese cambio, Plaza Houssay figuraba con 0 servicios y no como "sin dato", lo que contradice la regla del proyecto de no asumir que una estación sin dato no ofrece servicios.

Resolución, el 13 de octubre de 2026:

- Se quitó el paso de la consulta de `Dim_Estacion`. Plaza Houssay vuelve a figurar sin dato y su tooltip no muestra una cantidad.
- La medida del promedio se dejó robusta: excluye a las estaciones marcadas `SERVICIO_NULL`, sin depender de si su cantidad es 0 o vacía.
- Se repitieron las comprobaciones: 24 estaciones con dato, 191 relaciones, promedio de 7,96, y todas las demás comprobaciones del modelo en verde.

### Dashboard

| Control | Resultado |
|---|---|
| Totales de las tarjetas de las tres páginas | Coinciden con las medidas validadas |
| Filtros | Verificado con consultas equivalentes a los filtros: las medidas responden a tipo, estructura, comuna y servicio, y el mapa de estaciones responde al filtro de servicio. No se probaron los segmentadores con clics |
| Doble conteo | Ningún visual repite una dimensión. Las sumas por categoría dan el total |
| Claves técnicas | `id_estacion`, `numero_comuna`, `id_comuna`, `id_servicio` y la tabla puente están ocultos |
| Títulos y unidades | Todos los visuales con datos tienen título. Las tarjetas indican qué miden |
| Texto alternativo | Todos los visuales con datos lo tienen |
| Geografía | Las 25 estaciones caen dentro de la comuna y el barrio que declaran |
| Mapas y matriz | El autor confirmó en Power BI Desktop que el mapa de estaciones muestra 25 puntos, que el mapa de comunas muestra 15 círculos en tres tonos y que la matriz muestra los círculos |

### Lo que queda pendiente

- Capturas de pantalla de las tres páginas para la carpeta `images/`.
- Una revisión visual final de solapamientos y cortes de texto en cada página, con los filtros de tipo y de servicio aplicados.

## Fase 10: hallazgos y documentación

Los hallazgos están en [hallazgos.md](hallazgos.md), con la evidencia, la interpretación y la limitación de cada uno. Todas las cifras se recalcularon desde el modelo o desde el archivo de indicadores por comuna.

La documentación del proyecto queda en `docs/`: fuentes, modelo de datos, metodología, calidad, diseño y hallazgos.

## Fase 11: preparación para GitHub

| Elemento | Estado |
|---|---|
| README con la estructura propuesta | Listo |
| Licencia | MIT para el código y la documentación. Los datos conservan la licencia de su fuente |
| `.gitignore` | Excluye la caché y la configuración local de Power BI, los archivos temporales y los de Python |
| Dependencias de los scripts | `scripts/requirements.txt` |
| Archivos temporales en el repositorio | Ninguno |
| Credenciales o claves | Ninguna |

Puntos a decidir antes de publicar:

- **Ruta local en el modelo (resuelto).** El parámetro `RutaProyecto` quedó con un valor neutro (`C:\RUTA\AL\REPOSITORIO`), porque Power BI no admite rutas relativas para archivos locales. Hay que cambiarlo por la carpeta del repositorio antes de actualizar los datos.
- **Documentos de referencia (resuelto).** El PDF del manual de estilo del Gobierno de la Ciudad (2 MB) no se publica: queda excluido con `.gitignore`. Solo se versiona el documento de proyecto.
- **Capturas.** El README enlaza cuatro imágenes que todavía no existen en `images/`.
- **Nombre en la licencia.** Se usó "Joaquín Falcón".

## Anexo: dashboard en HTML

Fecha de la validación: 13 de octubre de 2026. Descripción en [diseno-dashboard.md](diseno-dashboard.md).

### Validación de los números

Se ejecutaron en un navegador los filtros del dashboard y se compararon los resultados con las medidas de Power BI Desktop.

| Prueba | Resultado en el HTML | Medida de Power BI |
|---|---|---|
| Sin filtros: estaciones, fijas, móviles y comunas con presencia | 25, 17, 8 y 15 / 15 | Igual |
| Servicio Control de Glucemia | 2 estaciones, 2 fijas, 0 móviles, 2 / 15 comunas | Igual |
| Servicio Control de Presión Arterial | 19 estaciones (16 fijas y 3 móviles), 13 / 15 comunas | Igual |
| Tipo móvil | 8 estaciones, 6 / 15 comunas | Igual |
| Comuna 13 | 2 estaciones móviles | Igual |
| Estructura carpa | 7 estaciones (1 fija y 6 móviles) | Igual |
| Barrio Caballito | 3 estaciones (2 fijas y 1 móvil) | Igual |
| Página 2 sin filtros: servicios, promedio, más y menos disponible | 15, 8,0, Actividad Física, Juegotecas y 1 más | Igual |
| Página 2, solo móviles | 7 servicios, 3,9, Actividad Física y 1 más, Asesoría Nutricional y 4 más | Igual |
| Página 2, solo fijas | 14 servicios, 10,0, Asesoría Nutricional y 3 más | Igual |
| Matriz de servicio por comuna | 15 filas y 134 círculos llenos | 134 celdas con servicio |
| Página 3: población, estaciones, estaciones cada 100.000 y habitantes por estación | 3.121.707, 25, 0,80 y 124.868 | Igual |
| Página 3, tipo móvil | 8 estaciones, 0,26 y 390.213 | Igual |
| Acceso Relativo de las 15 comunas | Mismos puntajes y posiciones | Igual (Comuna 6: 97,6; Comuna 1: 3,6) |

### Revisión visual

Se revisó en un navegador, con el diseño de escritorio y el de pantalla angosta:

- La portada, el encabezado, la navegación fija, las tarjetas, los filtros, los tres mapas y gráficos, la matriz y la tabla se muestran completos.
- La matriz cabe sin desplazamiento horizontal con las 15 comunas.
- El tema oscuro se probó con el atributo de tema: los colores de fijas y móviles se distinguen y los textos se leen.
- El panel de preguntas rápidas abre, muestra la respuesta y cierra.

### Problemas encontrados durante la construcción

- **Matriz cortada.** La primera versión mostraba solo cinco comunas porque la tarjeta era angosta. Se ensanchó la tarjeta y se redujo el espacio de las columnas.
- **Puntos superpuestos en la dispersión.** Las comunas 6 y 8 tienen valores casi idénticos y sus etiquetas se pisaban. Se agregó una regla que mueve las etiquetas a los costados cuando dos círculos se tocan, sin mover los puntos.
- **Etiquetas de comunas tapadas por las estaciones.** En el mapa de estaciones se achicaron.
- **Porcentaje sin decimal.** La cobertura de Servicios de Enfermería figuraba como "80 %" y no como "80,0 %". Se unificó el formato.

### Lo que no se probó

- La navegación con teclado, más allá de que los puntos y las comunas se pueden enfocar.
- Navegadores distintos del que se usó para la revisión.
- La impresión.
