# Metodología de los indicadores de acceso

Este documento explica cómo se miden el acceso a las Estaciones Saludables y la disponibilidad relativa por comuna. También justifica qué se incluyó en el indicador compuesto y qué se dejó afuera.

Los resultados son exploratorios. Describen la posición de cada comuna respecto de las demás, con los datos disponibles. No miden el acceso efectivo de las personas.

## Qué se mide y qué no

El proyecto usa cinco conceptos que no son equivalentes. Cada indicador pertenece a uno solo.

| Concepto | Qué responde | Indicador del proyecto | ¿Se mide? |
|---|---|---|---|
| Presencia | ¿Hay al menos una estación en la comuna? | Comunas con presencia (15 de 15) | Sí |
| Cobertura de superficie | ¿Qué parte del territorio queda cerca de una estación? | Cobertura a 500, 1.000 y 2.000 metros | Sí, por superficie |
| Disponibilidad de prestaciones | ¿Qué servicios declara cada estación? | Diversidad, cobertura territorial por servicio | Sí, según lo declarado en la fuente |
| Población potencialmente cercana | ¿Cuántas personas viven cerca de una estación? | Ninguno | No: haría falta la población por radio censal |
| Acceso efectivo | ¿Las personas usan los servicios cuando los necesitan? | Ninguno | No: no hay datos de uso, horarios, capacidad ni tiempos de viaje |

Por eso ningún resultado de este proyecto debe leerse como una medida de acceso efectivo ni de inequidad sanitaria.

## Tres dimensiones del acceso

| Dimensión | Pregunta | Indicadores |
|---|---|---|
| Acceso físico | ¿Hay una estación razonablemente cerca? | Estaciones por km², cobertura por radio, distancia media a la estación más cercana |
| Acceso a servicios | ¿La estación cercana ofrece lo que la persona necesita? | Cobertura de estaciones y de comunas por servicio, diversidad, cobertura por radio de un servicio básico y de uno escaso |
| Acceso poblacional | ¿La oferta es adecuada para la población? | Estaciones cada 100.000 habitantes, habitantes por estación, servicios cada 100.000 habitantes |

## Indicadores normalizados

Las medidas están en la carpeta `05 - Acceso` del modelo. Se leen por comuna, por tipo de estación o por servicio.

| Indicador | Cálculo | Qué conviene saber |
|---|---|---|
| Estaciones cada 100.000 habitantes | Estaciones sobre población, por 100.000 | Cuenta solo las estaciones ubicadas en la comuna |
| Estaciones fijas y móviles cada 100.000 habitantes | Igual, por tipo | Una móvil pesa lo mismo que una fija |
| Habitantes por estación | Población sobre estaciones | Vacío si la comuna no tiene estaciones |
| Estaciones por km² | Estaciones sobre superficie oficial | Pondera por superficie, no por población |
| Servicios cada 100.000 habitantes | Relaciones estación-servicio sobre población | Mezcla la cantidad de estaciones con la amplitud de su cartera |

## Cobertura por radio

Mide qué porcentaje de la superficie de la comuna queda a menos de 500, 1.000 y 2.000 metros de una estación. También calcula la distancia media a la estación más cercana.

El cálculo está en el script [analisis_acceso.py](../scripts/analisis_acceso.py) y escribe `data/processed/acceso_comunas_exploratorio.csv`, que el modelo lee. Si cambian las estaciones, hay que volver a ejecutar el script.

Método:

1. Se arma una grilla de puntos cada 50 metros dentro del polígono de cada comuna.
2. Para cada punto se calcula la distancia en línea recta a la estación más cercana.
3. La cobertura es el porcentaje de puntos que están dentro del radio.

Las estaciones de las comunas vecinas cuentan: una estación puede cubrir superficie de otra comuna. Un punto cubierto por dos estaciones se cuenta una sola vez, porque se usa la distancia a la más cercana.

### Sistema de coordenadas y distancias

Las estaciones y los polígonos vienen en CRS84 (longitud y latitud en grados, WGS84). El radio no se aplica sobre los grados: cada diferencia de coordenadas se convierte a metros antes de calcular la distancia.

- Un grado de latitud equivale a 110.933,5 metros y uno de longitud, a 91.713,7 metros. Son los radios de curvatura del elipsoide WGS84 (meridiano y primer vertical) en la latitud de referencia de la ciudad, 34,615° sur.
- La distancia es la hipotenusa de las dos diferencias en metros. En los 20 kilómetros que mide la ciudad, tratar esos factores como constantes produce un error menor que 2 metros cada 1.000.

Hasta el 13 de octubre de 2026 el script usaba 110.574 y 91.631,5 metros por grado, que son valores aproximados. La diferencia en sentido norte-sur era de 0,3 %. Al corregirlos, la cobertura de la ciudad a 1.000 metros pasó de 35,7 % a 35,6 % y la distancia media, de 1.421 a 1.424 metros. El orden de las comunas en cobertura no cambió, y la Disponibilidad Relativa de la Oferta tampoco.

### Verificación con un método independiente

Las pruebas automatizadas (`tests/test_proyecto.py`) recalculan la cobertura con otro método: proyectan los polígonos y las estaciones a metros, unen geométricamente los círculos de cada radio y miden el área de la intersección con cada comuna.

| Control | Resultado |
|---|---|
| Diferencia entre la grilla y la geometría exacta, por comuna y radio (45 comparaciones) | Menor que 0,5 puntos porcentuales en todas |
| Cobertura de la ciudad a 1.000 metros | 35,6 % con los dos métodos |
| Superficie de los polígonos proyectados | 204,4 km², igual al atributo de área de la fuente |
| Estaciones dentro del polígono de la comuna que declaran | 25 de 25 |

El total de la ciudad pondera la cobertura de cada comuna por la superficie oficial del censo (205,9 km²) y no por la del polígono (204,4 km²). La diferencia entre ambas ponderaciones es de 0,1 puntos porcentuales.

Los radios de 500, 1.000 y 2.000 metros son exploratorios, como indica el proyecto. No hay una norma que los justifique. Sirven para comparar comunas entre sí.

Limitaciones:

- La grilla pondera por superficie. Un parque o una zona sin vivienda pesa igual que una zona densa.
- La distancia en línea recta no equivale al tiempo de viaje real.
- La cobertura usa toda la red: no responde a los filtros de tipo de estación ni de servicio.

## Indicador compuesto: Disponibilidad Relativa de la Oferta

El proyecto pide no crear un índice arbitrario. Por eso primero se evaluaron las variables disponibles y se justificó cada decisión.

### Variables evaluadas

| Variable | Decisión | Motivo |
|---|---|---|
| Estaciones cada 100.000 habitantes | Incluida | Mide la oferta respecto de la población |
| Cobertura a 1.000 metros | Incluida | Mide la proximidad física, incluidas las estaciones de comunas vecinas |
| Diversidad de servicios | Incluida | Mide la amplitud de la oferta. Es la menos relacionada con las demás |
| Estaciones por km² | Excluida | Se parece demasiado a la cobertura a 1.000 metros (correlación de 0,94). Cuenta dos veces la misma dimensión |
| Servicios cada 100.000 habitantes | Excluida | Se parece a las estaciones cada 100.000 habitantes (0,79) y mezcla cantidad con cartera |
| Infraestructura (estructura de la estación) | Excluida | Falta en 2 de 25 estaciones y coincide casi por completo con el tipo: las fijas son estructuras y las móviles son carpas |
| Cobertura de un servicio básico o escaso | Fuera del compuesto | Se informa aparte. Referirse a un solo servicio limitaría el compuesto |

Correlación de Spearman entre los componentes candidatos, con las 15 comunas:

| | Estaciones cada 100.000 | Estaciones por km² | Cobertura a 1.000 m | Diversidad | Servicios cada 100.000 |
|---|---|---|---|---|---|
| Estaciones cada 100.000 | 1,00 | 0,84 | 0,70 | 0,36 | 0,79 |
| Estaciones por km² | 0,84 | 1,00 | 0,94 | 0,42 | 0,70 |
| Cobertura a 1.000 m | 0,70 | 0,94 | 1,00 | 0,57 | 0,68 |
| Diversidad | 0,36 | 0,42 | 0,57 | 1,00 | 0,57 |
| Servicios cada 100.000 | 0,79 | 0,70 | 0,68 | 0,57 | 1,00 |

### Cómo se calcula

Para cada comuna *c* se calculan tres componentes con toda la red de estaciones:

| Componente | Fórmula | Unidad | Dirección |
|---|---|---|---|
| Estaciones por habitante, *E* | estaciones ubicadas en *c* ÷ población de *c* × 100.000 | Estaciones cada 100.000 habitantes | Más alto, mayor disponibilidad |
| Cobertura de superficie, *K* | puntos de la grilla de *c* a 1.000 metros o menos de una estación ÷ puntos de la grilla de *c* | Proporción de 0 a 1 | Más alto, mayor disponibilidad |
| Diversidad, *D* | servicios distintos ofrecidos en *c* ÷ 15 servicios del catálogo observado | Proporción de 0 a 1 | Más alto, mayor disponibilidad |

Cada componente *x* se convierte en una posición relativa entre las 15 comunas:

```text
r(x_c) = (comunas con valor menor que x_c + (comunas con el mismo valor que x_c − 1) / 2) / 14
```

La comuna más baja recibe 0 y la más alta, 1. Los empates reciben el promedio de sus posiciones. El indicador es el promedio simple de las tres posiciones:

```text
Disponibilidad Relativa de la Oferta_c = 100 × (r(E_c) + r(K_c) + r(D_c)) / 3
```

- **Escala.** De 0 a 100. Solo valdría 100 una comuna que fuera la primera en los tres componentes.
- **Posición.** La comuna de mayor puntaje ocupa el puesto 1. Los puntajes se comparan con seis decimales y los empates comparten puesto (las comunas 2 y 12 comparten el tercero).
- **Grupos.** Las comunas en los puestos 1 a 5 forman el grupo de mayor disponibilidad relativa, las de los puestos 11 a 15 el de menor y el resto, el intermedio.
- **Valores faltantes.** No hay: las 15 comunas tienen estaciones, población y superficie. Una comuna sin estaciones recibiría 0 en estaciones por habitante y en diversidad.
- **Filtros.** El indicador no responde a los filtros del dashboard. Si respondiera, la posición de una comuna cambiaría al filtrar un tipo de estación y dejaría de ser comparable.

El resultado compara comunas entre sí. Una diferencia pequeña de puntaje no tiene un significado de magnitud, y un puntaje alto no indica que la oferta sea suficiente.

Se usan posiciones y no valores mínimos y máximos porque con 15 comunas los extremos distorsionan la escala. A cambio, se pierde la magnitud de las diferencias.

El indicador usa toda la red. No responde a los filtros de tipo de estación, estructura, barrio ni servicio.

### Pesos

Los tres componentes pesan lo mismo. No existe evidencia en los datos para asignarles pesos distintos, y cualquier valor sería una decisión arbitraria. En su lugar se midió cuánto cambia el resultado si los pesos cambian.

### Sensibilidad a los pesos

Se repitió el cálculo con 20.000 combinaciones de pesos al azar (sorteadas de forma uniforme entre todas las combinaciones que suman 1) y quitando un componente por vez.

| Comuna | Puntaje con pesos iguales | Posición | Rango de posición con pesos al azar (del 5 al 95 %) |
|---|---|---|---|
| 6 | 97,6 | 1 | 1 a 1 |
| 3 | 73,8 | 2 | 2 a 6 |
| 2 | 71,4 | 3 (empate) | 2 a 5 |
| 12 | 71,4 | 3 (empate) | 2 a 6 |
| 5 | 69,0 | 5 | 2 a 9 |
| 7 | 64,3 | 6 | 4 a 7 |
| 8 | 61,9 | 7 | 2 a 9 |
| 14 | 52,4 | 8 | 7 a 9 |
| 13 | 42,9 | 9 | 7 a 13 |
| 15 | 35,7 | 10 | 9 a 12 |
| 9 | 33,3 | 11 | 9 a 14 |
| 11 | 31,0 | 12 | 10 a 13 |
| 4 | 21,4 | 13 | 12 a 14 |
| 10 | 20,2 | 14 | 11 a 14 |
| 1 | 3,6 | 15 | 15 a 15 |

Lectura:

- La Comuna 6 queda primera y la Comuna 1 queda última en el 90 % central de las combinaciones de pesos, y también en las tres variantes sin un componente.
- Las comunas 4 y 10 quedan entre las últimas cinco en casi todas las variantes. La Comuna 10 sube al décimo lugar si se quita la diversidad, porque su debilidad es tener una sola estación móvil con dos servicios.
- El centro del ranking es sensible a los pesos: por ejemplo, la Comuna 8 puede ir del segundo al noveno lugar.
- Por eso las etiquetas del dashboard se basan en tercios y no en posiciones exactas. Las cinco primeras reciben "Mayor disponibilidad relativa", las cinco últimas "Menor disponibilidad relativa" y las cinco del medio "Disponibilidad relativa intermedia".

Las etiquetas describen la posición. No afirman que una comuna esté bien o mal atendida.

### Robustez frente a otras decisiones

El script [sensibilidad_disponibilidad_relativa.py](../scripts/sensibilidad_disponibilidad_relativa.py) compara el ordenamiento original con el de otras variantes justificables y escribe `data/processed/sensibilidad_disponibilidad_relativa.csv`. Ninguna variante reemplaza al indicador: sirven para saber qué resultados dependen de una decisión.

| Variante | Correlación de Spearman con el original | Tau de Kendall | Mayor cambio de puesto | Comunas que cambian de grupo |
|---|---|---|---|---|
| Pesos 50-25-25, con más peso en estaciones por habitante | 0,97 | 0,88 | 3 | 5, 8, 9 y 15 |
| Pesos 25-50-25, con más peso en cobertura de superficie | 0,98 | 0,90 | 2 | Ninguna |
| Pesos 25-25-50, con más peso en diversidad | 0,96 | 0,89 | 2 | 9 y 13 |
| Sin estaciones por habitante | 0,96 | 0,85 | 3 | 11 |
| Sin cobertura de superficie | 0,93 | 0,82 | 4 | 5, 8, 9 y 13 |
| Sin diversidad | 0,92 | 0,82 | 4 | 5, 7, 8, 10 y 12 |
| Normalización por mínimo y máximo, en lugar de posiciones | 0,95 | 0,85 | 4 | 5, 7, 8 y 12 |
| Normalización por puntaje z | 0,95 | 0,85 | 4 | 5, 7, 8 y 12 |
| Comunas 9 y 15 con un servicio más (campo truncado) | 0,97 | 0,90 | 2 | 9 y 13 |
| Comunas 9 y 15 con la cartera fija completa (14 de 15) | 0,97 | 0,90 | 2 | 9 y 13 |

Con los pesos al azar, la frecuencia con que cada comuna queda en un grupo extremo es:

| Grupo original | Comuna | Sorteos en que se mantiene en el grupo |
|---|---|---|
| Menor disponibilidad relativa | 1 | 100 % |
| | 4 | 100 % |
| | 10 | 99 % |
| | 11 | 89 % |
| | 9 | 54 % |
| Mayor disponibilidad relativa | 6 | 100 % |
| | 2 | 100 % |
| | 3 | 95 % |
| | 12 | 65 % |
| | 5 | 64 % |

Qué resultados son robustos y cuáles no:

- **Robusto.** La Comuna 6 queda primera y la Comuna 1, última, en todas las variantes. Las comunas 2 y 3 quedan en el grupo de mayor disponibilidad en casi todas. La Comuna 4 queda siempre en el de menor, y la Comuna 10 también, salvo cuando se quita la diversidad.
- **Bastante robusto.** La Comuna 11 se mantiene en el grupo de menor disponibilidad en el 89 % de los sorteos y sale de él solo si se quita el componente de estaciones por habitante.
- **Frágil.** La Comuna 9 integra el grupo de menor disponibilidad en el 54 % de los sorteos. Además, su única estación (Parque Avellaneda) tiene el campo de servicios posiblemente truncado: con un solo servicio más, pasa al grupo intermedio. Su lugar lo ocupa la Comuna 15, o la 13 si también se completa el dato de la Comuna 15. Las comunas 13 y 15 entran en ese grupo en el 28 % y el 30 % de los sorteos.
- **Frágil.** Las comunas 5 y 12 integran el grupo de mayor disponibilidad en dos de cada tres sorteos, y lo pierden frente a las comunas 7 y 8 si se normaliza por mínimo y máximo.

### Limitaciones propias del método de posiciones

- **La diversidad tiene solo cuatro valores distintos.** Las estaciones fijas ofrecen casi todas los mismos 10 servicios, así que nueve comunas empatan en 10 servicios de 15 (66,7 %), tres tienen 11 (73,3 %), una tiene 7 y dos tienen 2. Al convertir a posiciones, pasar de 10 a 11 servicios mueve a una comuna de 0,50 a 0,93 en ese componente: un servicio de diferencia equivale a 14 puntos del indicador. Con la normalización por mínimo y máximo, esa misma diferencia vale 4 puntos. Es el motivo por el que las comunas 5 y 12 cambian de grupo según el método.
- **Las posiciones ignoran la magnitud.** La Comuna 6 (1,48 estaciones cada 100.000 habitantes) y la Comuna 8 (1,47) quedan a una posición de distancia, igual que dos comunas separadas por una diferencia grande.
- **Promediar posiciones no mide acceso.** El indicador ordena comunas según tres rasgos de la oferta. No incorpora demanda, uso, horarios ni capacidad, y no permite afirmar que una diferencia de puntaje cause una diferencia en la salud de la población.
- **Los grupos extremos se parecen por construcción.** Como las estaciones por habitante son uno de los tres componentes, es esperable que el grupo de menor disponibilidad tenga menos estaciones por habitante. Esa diferencia describe cómo se armó el grupo: no es un hallazgo independiente.

### Sobre el nombre del indicador

El indicador se llamó "Acceso Relativo" hasta el 13 de octubre de 2026. La palabra "acceso" puede sugerir que mide el acceso efectivo de las personas, y no lo hace: ordena comunas según tres rasgos de la oferta declarada. Se renombró a **Disponibilidad Relativa de la Oferta**, que dice lo que mide: una disponibilidad (estaciones, cercanía y servicios), relativa (comparada entre las 15 comunas) y de la oferta (no de la demanda ni del uso).

El cambio alcanzó a las medidas del modelo (`Disponibilidad Relativa de la Oferta`, `Posicion Disponibilidad Relativa` y `Grupo de Disponibilidad Relativa`), a los visuales de Power BI que las usan, al dashboard web, a las pruebas y a la documentación. Los valores no cambiaron. Los documentos de auditoría anteriores a esa fecha pueden mencionar el nombre anterior cuando describen lo que se encontró en su momento.

### Alternativas metodológicas evaluadas

| Opción | Ventajas | Desventajas |
|---|---|---|
| Posiciones con pesos iguales (la actual) | No depende de valores extremos. Fácil de explicar. No requiere elegir una escala | Pierde la magnitud. Amplifica diferencias mínimas cuando hay muchos empates, como en la diversidad |
| Normalización por mínimo y máximo | Conserva la magnitud de las diferencias. Un servicio de diferencia pesa poco | Con 15 comunas, un valor extremo comprime al resto. La Comuna 6 fija el máximo de dos componentes |
| No usar un indicador compuesto y mostrar los tres componentes | No agrega supuestos. Evita lecturas causales | Se pierde el ordenamiento único que pide la pregunta "qué territorios analizar primero" |

La recomendación es mantener el método actual para el ordenamiento exploratorio y comunicar solo los resultados robustos: los dos extremos y las comunas 4, 10 y 11. Si en el futuro se incorporan más servicios o más estaciones, conviene reevaluar la normalización por mínimo y máximo.

## Limitaciones

- No hay datos de demanda, de personas atendidas, de capacidad ni de horarios.
- Las estaciones móviles no necesariamente están disponibles todos los días ni todo el día.
- Presencia de una estación no equivale a uso, y disponibilidad declarada no equivale a capacidad efectiva.
- La población es del Censo 2022 y las estaciones son de 2026. No se proyectó la población.
- Las dos estaciones con campo de servicios posiblemente truncado pueden tener más servicios que los registrados. Eso afecta a las comunas 9 y 15: con un servicio más, la Comuna 9 deja el grupo de menor disponibilidad relativa.
- La población se asigna por comuna. Una estación atiende también a personas de otras comunas y a quienes trabajan o pasan por la zona.
- Con 15 comunas, las diferencias pequeñas entre posiciones no son estadísticamente interpretables.
- La cobertura mide superficie, no población: no se sabe cuántas personas viven a menos de 1.000 metros de una estación.
