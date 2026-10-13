# Informe de auditoría integral

Auditoría del proyecto ya publicado: datos, indicadores, medidas DAX, indicador compuesto, geografía, conclusiones, dashboard web, documentación y publicación.

- **Fecha:** 13 de octubre de 2026.
- **Versión auditada:** commit `265bce2` de la rama `main`, igual a la publicada en GitHub.
- **Bitácora de la construcción:** el control de calidad de cada fase está en [qa.md](qa.md). Este documento no lo reemplaza.

## Resumen

- No se encontraron errores en los indicadores publicados: los diez valores de referencia y todos los indicadores por comuna coinciden con un recálculo independiente desde las fuentes y con el modelo de Power BI.
- Se encontraron dos problemas de prioridad alta, los dos de comunicación y no de cálculo: el proyecto podía confundirse con un producto oficial, y una conclusión presentaba como estable un resultado que no lo es (la ubicación de la Comuna 9).
- Se corrigieron un defecto latente en dos medidas DAX, una imprecisión de 0,3 % en la conversión de grados a metros, y cuatro problemas del dashboard web.
- Se agregaron 32 pruebas automatizadas, un análisis de robustez del indicador compuesto y un diccionario de datos.
- Quedan tres puntos sin verificar o sin resolver, todos fuera del alcance de una revisión de archivos. Están en [Pendientes](#pendientes-y-puntos-sin-verificar).
- Los cambios se publicaron el 13 de octubre de 2026, después de la aprobación del autor.

## 1. Alcance e inventario

| Componente | Archivos | ¿Reproducible? |
|---|---|---|
| Fuentes | `data/raw/`: 8 archivos de BA Data, INDEC e IDECBA | Sí: descarga manual documentada en [fuentes.md](fuentes.md) |
| Transformación | Power Query en `expressions.tmdl` y en las particiones de las tablas | Sí, con Power BI Desktop |
| Modelo | 4 tablas, 3 relaciones y 53 medidas en TMDL | Sí |
| Informe | 4 páginas y 48 visuales en PBIR | Sí. El aspecto final depende de Power BI Desktop y de ArcGIS |
| Cálculo espacial | `scripts/analisis_acceso.py` | Sí: un comando |
| Dashboard web | `scripts/construir_dashboard_html.py` y `plantilla_dashboard.html` generan `index.html` | Sí: un comando |
| Documentación | `README.md` y `docs/` | Manual |
| Despliegue | GitHub Pages desde la rama `main`, carpeta raíz, sin proceso de compilación | Automático al subir cambios |

Proceso manual que subsiste: en Power BI hay que cambiar el parámetro `RutaProyecto` por la carpeta local y actualizar los datos.

### Coherencia entre lo local y lo publicado

| Control | Resultado |
|---|---|
| Rama local contra `origin/main` | Mismo commit, sin cambios sin subir al iniciar la auditoría |
| `index.html` publicado contra el del repositorio | Idénticos (misma suma SHA-1) |
| CSV de estaciones publicado hoy en BA Data contra `data/raw/estaciones_saludables.csv` | Idénticos byte por byte (8.446 bytes, 25 filas) |
| Enlaces externos del README, la documentación y el dashboard (9) | Todos responden 200 |
| Enlaces locales del README y la documentación | Sin enlaces rotos (prueba automatizada) |
| Secretos o credenciales en el repositorio | No se encontraron |

## 2. Diagnóstico inicial

Calificación antes de modificar ningún archivo.

| Dimensión | Calificación inicial | Evidencia | Problemas | Prioridad |
|---|---|---|---|---|
| Problema de negocio | 4 | Pregunta central y nueve preguntas de negocio definidas en el README | Faltaba delimitar el alcance y para qué no sirve el análisis | Media |
| Estructura analítica | 4 | Tres secciones con una narrativa de presencia, servicios y brechas | Un hallazgo usaba los grupos del indicador como evidencia de una diferencia que surge en parte de su construcción | Media |
| Indicadores y modelado | 4 | Todos los indicadores coinciden con el recálculo independiente | Defecto latente en dos medidas DAX. Sin pruebas automatizadas | Media |
| Rigor metodológico | 3 | Sensibilidad a los pesos documentada | No se comunicaba la fragilidad de la Comuna 9. Sin validación independiente de la cobertura. Conversión de grados a metros aproximada. Efecto de los empates sin documentar | Alta |
| Visualización y UX | 4 | Dashboard web completo, con filtros, estados vacíos y navegación por teclado | Contraste insuficiente en una etiqueta. Barra de navegación de 208 píxeles en móvil. Aspecto de Power BI sin verificar | Media |
| Calidad del código | 3 | Scripts legibles y reproducibles con un comando | Ninguna prueba automatizada | Media |
| Documentación | 4 | Metodología, fuentes, modelo, hallazgos y bitácora de calidad | Sin diccionario de datos ni fórmulas formales. Hallazgos sin relevancia ni recomendaciones | Media |
| Publicación y portfolio | 3 | Repositorio, dashboard y portfolio en línea y coherentes entre sí | El proyecto podía confundirse con un producto oficial. Faltan capturas de Power BI en el README | Alta |

### Hallazgos de la auditoría

No hubo hallazgos bloqueantes.

| N.º | Prioridad | Hallazgo | Estado |
|---|---|---|---|
| A1 | Alta | Ningún texto aclaraba que el proyecto es independiente. La barra superior del dashboard decía "Ciudad Autónoma de Buenos Aires" y la portada lleva el logotipo de la Ciudad | Mitigado: aclaración en el dashboard, el README, los hallazgos y el portfolio. El logotipo de la portada queda a decisión del autor |
| A2 | Alta | Los hallazgos y el dashboard afirmaban que las cinco comunas de menor disponibilidad "son las mismas aunque cambien los pesos". La Comuna 9 se mantiene en ese grupo solo en el 54 % de las pruebas, y su único dato de servicios está posiblemente truncado | Corregido |
| A3 | Media | Las medidas "red completa" quitaban los filtros de seis columnas de la estación y no los de identificador, latitud, longitud y cantidad de servicios. Con un filtro sobre esas columnas, la Disponibilidad Relativa de la Oferta cambiaba. Ningún visual actual aplica esos filtros | Corregido y validado en el motor |
| A4 | Media | La conversión de grados a metros usaba 110.574 metros por grado de latitud. El valor del elipsoide WGS84 en la latitud de la ciudad es 110.933,5: una diferencia de 0,3 % | Corregido |
| A5 | Media | La cobertura espacial no se había contrastado con un método independiente | Resuelto: coincide con la geometría exacta |
| A6 | Media | No había pruebas automatizadas | Resuelto: 32 pruebas |
| A7 | Media | La diversidad tiene solo cuatro valores distintos entre las 15 comunas. El método de posiciones convierte un servicio de diferencia en 14 puntos del indicador | Documentado, con alternativa evaluada |
| A8 | Media | El hallazgo 1 usaba como evidencia que el grupo de menor disponibilidad tiene la mitad de las estaciones. Las estaciones por habitante son un componente del indicador que arma los grupos | Corregido: se reformuló y se movió a las limitaciones del hallazgo 7 |
| A9 | Media | En pantallas angostas la barra de navegación ocupaba cuatro filas y, al ser fija, tapaba un cuarto de la pantalla | Corregido |
| A10 | Media | La etiqueta del grupo intermedio tenía un contraste de 3,3 a 1. El mínimo es 4,5 | Corregido: 4,8 a 1 |
| A11 | Media | El portfolio hablaba de "equidad territorial" y de un dashboard que "prioriza territorios" | Corregido |
| A12 | Media | El nombre "Acceso Relativo" puede sugerir que mide acceso efectivo | Corregido: renombrado a "Disponibilidad Relativa de la Oferta" |
| A13 | Media | El README no muestra capturas reales de las páginas de Power BI | Pendiente: requiere capturas del autor |
| A14 | Media | El aspecto del informe de Power BI nunca fue verificado por el revisor, incluido el cambio de paleta | Pendiente: requiere revisión visual en Power BI Desktop |
| A15 | Baja | La consola del navegador registraba un error 404 por la falta de ícono | Corregido |
| A16 | Baja | Las tablas del dashboard no tenían nombre accesible y no había enlace para saltar al contenido | Corregido |
| A17 | Baja | La tipografía bloqueaba el primer dibujado de la página | Corregido |
| A18 | Baja | El script de análisis asignaba posiciones distintas a comunas empatadas al imprimir la sensibilidad | Corregido |
| A19 | Baja | Sin metadatos para compartir el enlace en redes | Corregido |
| A20 | Baja | La columna `categoria_servicio` de `Dim_Servicio` está vacía | Sin cambios: está documentada como reservada |

## 3. Validación de datos

Todas las verificaciones de esta sección son pruebas automatizadas de `tests/test_proyecto.py`.

| Control | Resultado |
|---|---|
| Registros de estaciones en el CSV, en el GeoJSON, en `Dim_Estacion` y en el dashboard | 25 en los cuatro |
| Identificadores y nombres de estación | Únicos |
| Nulos en identificador, nombre, tipo, estructura, dirección, barrio y comuna | Ninguno |
| Atributos del CSV contra los del GeoJSON | Iguales en las 25 estaciones |
| Coordenadas del CSV (WKT) contra las del GeoJSON | Iguales |
| Sistema de referencia | CRS84 en estaciones y comunas |
| Estaciones dentro del recuadro de la ciudad | 25 de 25 |
| Estaciones dentro del polígono de la comuna que declaran | 25 de 25 |
| Polígonos de comunas | 15, válidos y sin superposición |
| Pares estación-servicio en la tabla puente | 191, sin duplicados |
| Filas huérfanas en la tabla puente (medidas de QA del modelo) | 0 |
| Población de las 15 comunas | Suma 3.121.707, igual al total del cuadro del INDEC |

Registros con problemas de calidad, ya documentados en [qa.md](qa.md), y su tratamiento:

| Estación | Problema | Tratamiento | Efecto |
|---|---|---|---|
| Plaza Houssay | Campo de servicios vacío | No aporta filas a la tabla puente. Se excluye del promedio de servicios | El promedio de las fijas es 10,0 sobre 16 estaciones. Con Houssay en cero sería 9,4 |
| Parque Los Andes | Campo cortado en 254 bytes. Termina en "Actividade" | Se descarta el fragmento cortado. No se completa el texto | La Comuna 15 figura sin Actividad Física |
| Parque Avellaneda | Campo de 254 bytes exactos. Su último servicio está completo | Se conservan los 10 servicios | Puede tener más servicios sin registrar |

Ningún registro se excluye del conteo de estaciones.

**Normalización de coordenadas.** El proyecto no corrige coordenadas. No hay divisiones por potencias de diez ni reglas de reparación: la latitud y la longitud se leen tal como vienen en el GeoJSON, y las 25 son válidas. No hubo anomalías que registrar.

## 4. Verificación de indicadores

### Valores de referencia

| Indicador | Referencia | Recálculo independiente | Modelo de Power BI | Dashboard web |
|---|---|---|---|---|
| Total de estaciones | 25 | 25 | 25 | 25 |
| Estaciones fijas | 17 | 17 | 17 | 17 |
| Estaciones móviles | 8 | 8 | 8 | 8 |
| Comunas con presencia | 15 de 15 | 15 de 15 | 15 / 15 | 15 / 15 |
| Servicios diferentes | 15 | 15 | 15 | 15 |
| Promedio de servicios por estación | 8,0 | 7,958 | 7,958 | 8,0 |
| Servicios por estación fija | 10,0 | 10,000 | 10,000 | 10,0 |
| Servicios por estación móvil | 3,9 | 3,875 | 3,875 | 3,9 |
| Servicios distintos en fijas | 14 | 14 | 14 | 14 |
| Servicios distintos en móviles | 7 | 7 | 7 | 7 |

Los diez coinciden. No hubo que modificar ningún cálculo.

### Definición de cada indicador

| Indicador | Fórmula | Unidad | Granularidad | Denominador | Contexto de filtro | Valor de la ciudad |
|---|---|---|---|---|---|---|
| Estaciones cada 100.000 habitantes | Estaciones ÷ población × 100.000 | Estaciones cada 100.000 habitantes | Comuna o ciudad | Población del Censo 2022. No cambia con los filtros de estaciones | Responde a tipo, estructura, barrio y servicio | 0,80 |
| Habitantes por estación | Población ÷ estaciones | Personas | Comuna o ciudad | Estaciones del contexto. Vacío si no hay | Igual que el anterior | 124.868 |
| Diversidad de servicios | Servicios distintos ÷ servicios del catálogo observado | Porcentaje | Comuna, estación o tipo | 15 servicios. Fijo | Responde a los filtros de estaciones | 100 % |
| Cobertura territorial por servicio | Comunas con el servicio ÷ comunas de la ciudad | Porcentaje | Servicio | 15 comunas. Fijo, aunque haya una comuna seleccionada | Responde a tipo y estructura | De 6,7 % a 93,3 % |
| Comunas con disponibilidad | Comunas con al menos una estación que ofrece el servicio | Comunas | Servicio | No aplica | Responde a tipo y estructura | De 1 a 14 |
| Cobertura espacial a 1.000 metros | Puntos de la grilla a 1.000 metros o menos de una estación ÷ puntos de la grilla | Porcentaje de superficie | Comuna. La ciudad pondera por superficie oficial | Superficie de la comuna | No responde a los filtros: usa toda la red | 35,6 % |
| Disponibilidad Relativa de la Oferta | 100 × promedio de las posiciones relativas de tres componentes | Puntaje de 0 a 100 | Comuna. Vacío con más de una comuna | 14, la cantidad de comunas menos una | No responde a los filtros: usa toda la red | No aplica |

Las fórmulas completas están en [metodologia.md](metodologia.md).

### Resultados por comuna

Recalculados desde las fuentes y comparados con el modelo de Power BI y con el dashboard. Coinciden en las 15 comunas.

| Comuna | Estaciones | Cada 100.000 habitantes | Cobertura a 1.000 m | Diversidad | Disponibilidad Relativa de la Oferta | Puesto |
|---|---|---|---|---|---|---|
| 1 | 1 | 0,45 | 10,9 % | 13,3 % | 3,6 | 15 |
| 2 | 2 | 1,24 | 58,7 % | 66,7 % | 71,4 | 3 |
| 3 | 2 | 1,02 | 81,8 % | 66,7 % | 73,8 | 2 |
| 4 | 1 | 0,44 | 21,8 % | 66,7 % | 21,4 | 13 |
| 5 | 1 | 0,51 | 67,8 % | 73,3 % | 69,0 | 5 |
| 6 | 3 | 1,48 | 82,3 % | 73,3 % | 97,6 | 1 |
| 7 | 2 | 0,93 | 51,7 % | 66,7 % | 64,3 | 6 |
| 8 | 3 | 1,47 | 34,6 % | 66,7 % | 61,9 | 7 |
| 9 | 1 | 0,59 | 17,6 % | 66,7 % | 33,3 | 11 |
| 10 | 1 | 0,58 | 23,4 % | 13,3 % | 20,2 | 14 |
| 11 | 1 | 0,49 | 27,4 % | 66,7 % | 31,0 | 12 |
| 12 | 2 | 0,84 | 40,0 % | 73,3 % | 71,4 | 3 |
| 13 | 2 | 0,76 | 43,1 % | 46,7 % | 42,9 | 9 |
| 14 | 2 | 0,80 | 39,7 % | 66,7 % | 52,4 | 8 |
| 15 | 1 | 0,51 | 29,6 % | 66,7 % | 35,7 | 10 |

## 5. Validación de medidas DAX

El modelo se abrió en Power BI Desktop, se actualizó con los datos del repositorio y se consultó con DAX. No se guardó ningún cambio desde Desktop.

| Control | Resultado |
|---|---|
| Filas: `Dim_Estacion`, `Dim_Servicio`, `Bridge_Estacion_Servicio` y `Dim_Comuna` | 25, 15, 191 y 15 |
| Pares estación-servicio distintos en la tabla puente | 191: sin duplicados que multipliquen registros |
| Medidas de QA: huérfanas de estación, huérfanas de servicio y estaciones sin coordenadas | 0, 0 y 0 |
| Suma de estaciones por comuna contra el total | 25 en los dos |
| Celdas con servicio en la matriz de servicio por comuna | 134, igual al recálculo |
| Estaciones y comunas por servicio, en los 15 servicios | Iguales al recálculo |
| Promedio de servicios con el filtro de tipo | 10,000 en fijas y 3,875 en móviles |
| Población con filtros de tipo o de servicio | No cambia: el denominador es fijo |
| Disponibilidad Relativa de la Oferta y posición de las 15 comunas | Iguales al recálculo, con todos los decimales |
| Disponibilidad Relativa de la Oferta con filtro de tipo, de servicio o de ambos | No cambia |
| Disponibilidad Relativa de la Oferta con filtro de latitud, cantidad de servicios o identificador de estación | **Cambiaba** antes de la corrección. No cambia después |
| Disponibilidad Relativa de la Oferta y posición con más de una comuna en el contexto | Vacíos, como está definido |
| Divisiones | Todas usan `DIVIDE`: una comuna sin estaciones da vacío y no error |

Rendimiento, medido con las métricas de ejecución del motor: la consulta de la tabla de indicadores por comuna tarda 22 milisegundos y la de la matriz de servicio por comuna (225 celdas), 4 milisegundos. Con 25 estaciones y 191 filas en la tabla puente, no hay nada que optimizar. No se usó el Analizador de rendimiento de Power BI Desktop, que requiere operar la interfaz.

Revisión de las 53 medidas:

- No hay medidas redundantes. Las dos medidas "red completa" existen porque el indicador compuesto necesita ignorar los filtros del usuario.
- La única corrección funcional es la del hallazgo A3. No se cambió ninguna medida por estilo.
- Las tres relaciones filtran en un solo sentido. No hay relaciones bidireccionales ni referencias cíclicas.

## 6. Auditoría del indicador Disponibilidad Relativa de la Oferta

La definición matemática, la normalización, los pesos, la dirección de los componentes y el tratamiento de empates están en [metodologia.md](metodologia.md). Esta sección resume lo que se comprobó.

| Aspecto | Comprobación |
|---|---|
| Fórmula | El recálculo con otra implementación da los mismos 15 puntajes que el script, el modelo y el dashboard |
| Escala | Todos los puntajes están entre 0 y 100. El mínimo es 3,6 y el máximo, 97,6 |
| Dirección | En los tres componentes, un valor más alto es mayor disponibilidad |
| Empates | Las comunas 2 y 12 empatan en 71,4 y comparten el puesto 3. Hay cinco comunas en cada grupo extremo |
| Valores faltantes | No hay: las 15 comunas tienen los tres componentes |
| Filtros | No responde a ningún filtro del dashboard, tras la corrección A3 |

### Prueba de sensibilidad

Se calcularon once variantes y 20.000 combinaciones de pesos al azar con `scripts/sensibilidad_disponibilidad_relativa.py`. La tabla completa está en [metodologia.md](metodologia.md).

| Resultado | Estabilidad |
|---|---|
| Comuna 6 primera y Comuna 1 última | En todas las variantes |
| Correlación de Spearman con el ordenamiento original | Entre 0,92 y 0,98 |
| Comunas 1, 4 y 10 en el grupo de menor disponibilidad | En el 99 % o más de los sorteos |
| Comuna 11 en el grupo de menor disponibilidad | 89 % de los sorteos |
| Comuna 9 en el grupo de menor disponibilidad | 54 % de los sorteos. Sale del grupo si Parque Avellaneda tuviera un servicio más |
| Comunas 5 y 12 en el grupo de mayor disponibilidad | 64 % y 65 % de los sorteos. Salen del grupo con la normalización por mínimo y máximo |
| Comunas que más cambian de puesto | 5 y 8: del puesto 2 al 9 |

La sensibilidad no reemplaza al indicador. Sirvió para corregir cómo se comunica: ahora los textos presentan como robustos solo los dos extremos y las comunas 4, 10 y 11.

### Propuesta que requiere decisión del autor

1. **Reevaluar la normalización por mínimo y máximo** si se suman estaciones o servicios. Ventaja: un servicio de diferencia deja de pesar 14 puntos. Costo: con 15 comunas, un valor extremo comprime al resto.

No se implementó. El renombre del indicador, que también se propuso en esta auditoría, se aplicó después por decisión del autor (A12).

## 7. Validación geográfica

| Control | Resultado |
|---|---|
| Sistema de referencia de las coordenadas | CRS84 en las dos capas, declarado en los archivos |
| Radio aplicado sobre grados | No. Las diferencias se convierten a metros antes de medir |
| Factores de conversión | Corregidos a los radios de curvatura del elipsoide WGS84 en 34,615° sur |
| Asignación de estaciones a comunas | 25 de 25 dentro del polígono declarado |
| Superficies superpuestas | No se cuentan dos veces: se usa la distancia a la estación más cercana. La unión geométrica de los 25 círculos de 1.000 metros es menor que la suma de sus áreas |
| Fuente de los límites comunales | BA Data, documentada en [fuentes.md](fuentes.md) |
| Cobertura por comuna contra geometría exacta, tres radios | 45 comparaciones con diferencias menores que 0,5 puntos porcentuales |
| Cobertura de la ciudad a 1.000 metros | 35,6 % con la grilla y con la geometría exacta |
| Superficie de los polígonos proyectados | 204,4 km², igual al atributo de área de la fuente |
| Posición de las estaciones en el mapa del dashboard web | Proyección cilíndrica local a partir de las mismas coordenadas |

Efecto de la corrección de los factores de conversión:

| Indicador de la ciudad | Antes | Después |
|---|---|---|
| Cobertura a 500 metros | 9,6 % | 9,6 % |
| Cobertura a 1.000 metros | 35,7 % | 35,6 % |
| Cobertura a 2.000 metros | 79,1 % | 79,0 % |
| Distancia media a la estación más cercana | 1.421 m | 1.424 m |
| Orden de las comunas en cobertura a 1.000 metros | | Sin cambios |
| Disponibilidad Relativa de la Oferta de las 15 comunas | | Sin cambios |

Los cinco conceptos que no deben confundirse (presencia, cobertura de superficie, disponibilidad de prestaciones, población potencialmente cercana y acceso efectivo) están diferenciados en [metodologia.md](metodologia.md). El proyecto mide los tres primeros.

## 8. Matriz de conclusiones

Dictamen sobre las afirmaciones publicadas antes de la auditoría.

| Conclusión original | Indicador de respaldo | Evidencia | Limitaciones | Dictamen | Redacción corregida |
|---|---|---|---|---|---|
| Las 15 comunas tienen al menos una estación | Comunas con presencia | 15 de 15 | No demuestra cobertura de la población | PASS | Se agregó que presencia no equivale a cobertura de la población |
| Siete comunas dependen de una sola estación y tres no tienen ninguna fija | Estaciones por comuna y tipo | Comunas 1, 4, 5, 9, 10, 11 y 15; comunas 1, 10 y 13 | Ninguna adicional | PASS | Sin cambios |
| Los dos grupos extremos tienen población casi igual y 10 contra 5 estaciones | Disponibilidad Relativa de la Oferta | 992.086 y 999.462 habitantes | Los grupos se arman, en parte, con las estaciones por habitante | WARN | Pasó de evidencia del hallazgo 1 a limitación del hallazgo 7 |
| "Una persona de la Comuna 4 comparte su estación con más de tres veces más vecinos" | Habitantes por estación | 229.240 contra 67.681: cociente de 3,4 | Supone que la gente usa la estación de su comuna | WARN | "En la Comuna 4 hay 3,4 veces más habitantes por cada estación que en la Comuna 6" |
| La oferta por habitante varía más de tres veces | Estaciones cada 100.000 habitantes | De 0,44 a 1,48 | Cuenta estaciones, no capacidad | PASS | Se precisó: "cantidad de estaciones por habitante" |
| Los controles básicos llegan a 13 comunas y el Control de Glucemia, a 2 | Comunas con servicio | Verificado en toda la red, sin filtros | Campos truncados en las comunas 9 y 15 | PASS | Sin cambios |
| Fijas 10,0 servicios en promedio y móviles 3,9 | Promedio de servicios por estación | 10,000 y 3,875 | Excluye a Plaza Houssay. Solo ocho móviles | PASS | Se agregaron la composición de las carteras y el valor con Houssay en cero |
| "El tipo de estación define la amplitud de la oferta" | Promedio por tipo | Diferencia de 6,1 servicios | "Define" sugiere causa | WARN | "Las estaciones fijas ofrecen una cartera más amplia que las móviles" |
| Las móviles "no compensan la falta de servicios" | Diversidad por comuna | 13,3 % en las comunas 1 y 10 | No se sabe si los vecinos usan fijas de comunas vecinas | WARN | "En tres comunas la única presencia es móvil y con cartera reducida" |
| El 35,7 % de la superficie está a menos de 1.000 metros | Cobertura a 1.000 metros | 35,6 % tras la corrección | Mide superficie, no población | PASS, con valor corregido | 35,6 % |
| "Hay comunas lejos de cualquier estación" | Distancia media | Comuna 9: 2.444 metros | Línea recta, por superficie | WARN | Se reemplazó por los valores mínimo y máximo de cobertura |
| "Las comunas con menor disponibilidad relativa son las mismas aunque cambien los pesos" | Sensibilidad | Cierto para 1, 4, 10 y 11. La Comuna 9 se mantiene en el 54 % | Dato truncado en la Comuna 9 | FAIL | "El ordenamiento exploratorio es estable en los extremos y sensible en el centro" |
| "Conviene analizar primero las comunas 1, 10, 4, 11 y 9" | Disponibilidad Relativa de la Oferta | Robusto para cuatro de las cinco | Indicador exploratorio | WARN | "Comenzar por las comunas 1, 4, 10 y 11" y completar antes el dato de la Comuna 9 |
| Portfolio: "Equidad territorial de las Estaciones Saludables" | Ninguno | El proyecto no mide equidad | Sin datos de demanda ni de uso | FAIL | "Distribución territorial de la oferta" |
| Portfolio: "un dashboard que prioriza territorios" | Disponibilidad Relativa de la Oferta | Ordena de forma exploratoria | No sirve para asignar recursos | WARN | "ordena, de forma exploratoria, qué comunas conviene analizar primero" |
| Conclusión: "La pregunta central no tiene una respuesta afirmativa sencilla" | Todos | Hay diferencias medibles en la oferta | No se puede afirmar ni negar equidad | PASS | Se explicitó que no se concluye equidad ni inequidad |

Resultado: 7 PASS, 7 WARN y 2 FAIL. Los dos FAIL y los siete WARN se corrigieron en el texto. Ningún resultado numérico se modificó para ajustarlo a una conclusión.

Los siete hallazgos de [hallazgos.md](hallazgos.md) tienen ahora la misma estructura: hallazgo cuantitativo, evidencia, interpretación, relevancia para la planificación, limitación y recomendación. Cada recomendación indica si está respaldada por los datos o si es una hipótesis a investigar.

## 9. Dashboard web

### Pruebas funcionales

Ejecutadas en un navegador automatizado sobre la versión corregida.

| Prueba | Resultado |
|---|---|
| Indicadores iniciales de las tres secciones | Iguales al modelo de Power BI |
| Filtro combinado sin resultados (tipo móvil y Control de Glucemia) | Indicadores en cero y mensaje "Ninguna estación cumple los filtros" en los tres gráficos |
| Botón para limpiar filtros | Restablece los valores iniciales |
| Filtro combinado con resultados (Comuna 6 y tipo fija) | 2 estaciones, 1 de 15 comunas y 2 puntos en el mapa |
| Filtro de tipo en la sección de brechas | Cambian estaciones e indicadores por habitante. La Disponibilidad Relativa de la Oferta no cambia |
| Navegación con teclado | Los 25 puntos del mapa y las 15 comunas reciben foco, tienen etiqueta y muestran el detalle. Enter selecciona una comuna |
| Estructura de encabezados | Un título principal, tres secciones y sus tarjetas, sin saltos de nivel |
| Escritorio (1.440 px) | Sin desplazamiento horizontal. Las tablas entran completas |
| Móvil (390 px) | Sin desplazamiento horizontal de la página. Las grillas pasan a una columna y las tablas se desplazan dentro de su tarjeta |
| Barra de navegación en móvil | 57 píxeles de alto. Antes, 208 |

No se probaron lectores de pantalla ni navegadores distintos de Chromium.

### Lighthouse

Lighthouse 12.8.2 con Chrome sin interfaz, una ejecución por caso. Las dos versiones se sirvieron desde el mismo servidor local, para que la comparación no dependa de la red.

| Versión | Dispositivo | Rendimiento | Accesibilidad | Buenas prácticas | SEO | Primer dibujado | Mayor elemento | Auditorías fallidas |
|---|---|---|---|---|---|---|---|---|
| Antes | Escritorio | 97 | 96 | 96 | 100 | 1,0 s | 1,0 s | Contraste y error de consola |
| Después | Escritorio | 100 | 100 | 100 | 100 | 0,4 s | 0,7 s | Ninguna |
| Antes | Móvil | 80 | 96 | 96 | 100 | 3,6 s | 3,6 s | Contraste y error de consola |
| Después | Móvil | 95 | 100 | 100 | 100 | 2,0 s | 2,7 s | Ninguna |

Mediciones sobre GitHub Pages, que incluyen la red real:

| Versión publicada | Dispositivo | Rendimiento | Accesibilidad | Buenas prácticas | SEO | Primer dibujado |
|---|---|---|---|---|---|---|
| Antes | Escritorio | 93 | 96 | 96 | 100 | 1,3 s |
| Después (dos ejecuciones) | Escritorio | 91 y 92 | 100 | 100 | 100 | 1,4 s |
| Antes | Móvil | 81 | 96 | 96 | 100 | 3,5 s |
| Después (dos ejecuciones) | Móvil | 83 y 83 | 100 | 100 | 100 | 3,5 s |

En producción mejoraron la accesibilidad y las buenas prácticas, que llegaron a 100. El rendimiento quedó igual, dentro de la variación entre ejecuciones: la mejora medida en el servidor local no se trasladó, porque el tiempo de carga lo domina la descarga del archivo único de 247 KB. Para mejorarlo habría que sacar la portada del HTML y servirla como imagen aparte, lo que rompe el diseño de archivo único. No se hizo.

El dashboard es un único archivo HTML de 247 KB, sin bibliotecas. El mayor componente es la portada incrustada (169 KB). No depende de servicios de mapas externos: los mapas se dibujan en SVG con los polígonos del repositorio. La única dependencia externa es la tipografía, que tiene alternativa del sistema.

## 10. Power BI

| Aspecto | Resultado |
|---|---|
| Modelo en estrella con tabla puente | 4 tablas y 3 relaciones de uno a muchos, de filtro simple |
| Tipos de datos | Claves enteras, coordenadas decimales con categoría de latitud y longitud |
| Consultas de Power Query | Tres capas (origen, preparación y modelo), sin transformaciones duplicadas ni referencias cíclicas |
| Columnas innecesarias | `categoria_servicio` está vacía y documentada como reservada. `servicio` en la tabla puente está oculta y se usa para control |
| Columnas calculadas en DAX | Ninguna: todo se calcula en Power Query o en medidas |
| Carga del modelo corregido | El archivo TMDL modificado abre en Power BI Desktop y actualiza sin errores |
| Archivos PBIR | Sin cambios en esta auditoría |
| Navegación entre las tres páginas y la portada | Sin cambios. Validada contra los esquemas en la fase 8 |

No se pudo verificar: el aspecto de las páginas, las interacciones con clics entre visuales y los mapas de ArcGIS. Requieren operar Power BI Desktop.

## 11. Registro de cambios

### Correcciones funcionales

| Archivo | Cambio | Motivo | Efecto sobre los indicadores |
|---|---|---|---|
| `powerbi/.../tables/_Medidas.tmdl` | Las dos medidas "red completa" quitan también los filtros de identificador, latitud, longitud y cantidad de servicios | A3 | Ninguno en los visuales actuales. La Disponibilidad Relativa de la Oferta ya no cambia con esos filtros |
| `scripts/analisis_acceso.py` | Factores de grados a metros del elipsoide WGS84. Posiciones compartidas en los empates al imprimir | A4 y A18 | Cobertura de la ciudad a 1.000 metros de 35,7 % a 35,6 %. Disponibilidad Relativa de la Oferta sin cambios |
| `data/processed/acceso_comunas_exploratorio.csv` | Regenerado | A4 | Cambian las seis columnas de cobertura y distancia, en menos de 0,4 puntos porcentuales |
| `scripts/sensibilidad_disponibilidad_relativa.py` y `data/processed/sensibilidad_disponibilidad_relativa.csv` | Nuevos | A2 y A7 | Ninguno: miden la robustez del indicador |
| `tests/test_proyecto.py` | Nuevo: 32 pruebas | A5 y A6 | Ninguno |
| `scripts/construir_dashboard_html.py` | La respuesta sobre qué comunas analizar primero informa cuáles se mantienen en el grupo | A2 | Ninguno |

### Cambios visuales y de accesibilidad

| Archivo | Cambio | Motivo |
|---|---|---|
| `scripts/plantilla_dashboard.html` | Aclaración de proyecto independiente en la barra superior, el encabezado y el pie | A1 |
| | Etiqueta del grupo intermedio con contraste de 4,8 a 1 | A10 |
| | Navegación en una fila con desplazamiento horizontal en pantallas angostas | A9 |
| | Ícono incrustado, metadatos para compartir, tipografía sin bloqueo, enlace para saltar al contenido y nombre accesible de las tablas | A15, A16, A17 y A19 |
| | Nota metodológica con los resultados robustos de la sensibilidad | A2 |
| `index.html` | Regenerado | |

### Documentación

| Archivo | Cambio |
|---|---|
| `README.md` | Aclaración de proyecto independiente, autor, tabla de alcance, fechas de las fuentes, hallazgos reformulados, mapa de la documentación, pruebas y valor corregido de cobertura |
| `docs/metodologia.md` | Conceptos que se miden y que no, sistema de coordenadas, verificación independiente, fórmulas, robustez, limitaciones del método, nombre del indicador y alternativas |
| `docs/hallazgos.md` | Reescrito con la estructura de seis partes y los dictámenes de la matriz de conclusiones |
| `docs/diccionario-datos.md` | Nuevo |
| `docs/QA_REPORT.md` | Nuevo: este documento |
| `docs/fuentes.md`, `docs/qa.md` y `docs/diseno-dashboard.md` | Verificación de la fuente al 13 de octubre, nota de actualización y cambios del dashboard web |

### Portfolio

En el repositorio `joacofalcon58.github.io`: subtítulo, resultado, un hallazgo y el enlace al informe de auditoría del caso (A11).

## 12. Evaluación final

| Dimensión | Antes | Después | Fundamento | Qué queda sin verificar |
|---|---|---|---|---|
| Problema de negocio | 4 | 5 | Objetivo, población, alcance y usos definidos en el README | Nada |
| Estructura analítica | 4 | 5 | Tres secciones con narrativa coherente. Hallazgos sin circularidad | Nada |
| Indicadores y modelado | 4 | 5 | Fórmulas documentadas. 32 pruebas. Coincidencia entre fuentes, modelo y dashboard | Nada |
| Rigor metodológico | 3 | 5 | Indicador auditado, robustez medida, cobertura validada con otro método y limitaciones explícitas | Nada |
| Visualización y UX | 4 | 4 | Dashboard web sin fallas en las pruebas y con 100 en accesibilidad | El informe de Power BI no se verificó visualmente. Por eso no llega a 5 |
| Calidad del código | 3 | 5 | Reproducible con cuatro comandos. Pruebas automatizadas. Sin defectos conocidos | Nada |
| Documentación | 4 | 5 | Metodología, diccionario, hallazgos, fuentes e informe de auditoría | Nada |
| Publicación y portfolio | 3 | 4 | Repositorio, dashboard y portfolio publicados, coherentes y con enlaces válidos | Faltan capturas de Power BI. Queda la decisión sobre el logotipo |

No queda ningún hallazgo bloqueante ni de prioridad alta sin tratar. El hallazgo A1 pasó de prioridad alta a media: la aclaración está en todos los textos, pero el logotipo sigue en la portada.

## Pendientes y puntos sin verificar

| Punto | Por qué no se resolvió | Qué hace falta |
|---|---|---|
| Aspecto e interacciones del informe de Power BI (A14) | No se puede ver el informe renderizado sin operar Power BI Desktop | Abrir el informe, actualizar los datos, revisar las cuatro páginas y guardar |
| Capturas de las páginas de Power BI en el README (A13) | Dependen del punto anterior | Tres capturas en `images/` |
| Logotipo de la Ciudad en la portada (A1) | Es una decisión de diseño del autor sobre una imagen propia | Decidir si se quita el logotipo de la portada |
| Lectores de pantalla y otros navegadores | Fuera del entorno de prueba | Prueba manual |

## Publicación

- **Estado.** El 13 de octubre de 2026, con autorización del autor, se subieron los cambios de este repositorio y después los del portfolio. El `index.html` publicado es idéntico al del repositorio.
- **Pasos seguidos, válidos para próximas publicaciones:**
  1. Ejecutar `python -m unittest discover -s tests -v` y confirmar que pasan las 32 pruebas.
  2. Subir la rama `main` de este repositorio. GitHub Pages publica `index.html` sin pasos adicionales.
  3. Verificar que el dashboard publicado muestre 35,6 % en la documentación y la aclaración de proyecto independiente.
  4. Subir después el portfolio, porque enlaza a `docs/QA_REPORT.md` de este repositorio.
  5. En Power BI Desktop, cambiar `RutaProyecto`, actualizar los datos y guardar, para que el informe tome los valores regenerados de cobertura.
