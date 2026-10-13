# Metodología de los indicadores de acceso

Este documento explica cómo se miden el acceso a las Estaciones Saludables y la disponibilidad relativa por comuna. También justifica qué se incluyó en el indicador compuesto y qué se dejó afuera.

Los resultados son exploratorios. Describen la posición de cada comuna respecto de las demás, con los datos disponibles. No miden el acceso efectivo de las personas.

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

Las estaciones de las comunas vecinas cuentan: una estación puede cubrir superficie de otra comuna. Las distancias usan una aproximación local de grados a metros, adecuada para esta escala.

Los radios de 500, 1.000 y 2.000 metros son exploratorios, como indica el proyecto. No hay una norma que los justifique. Sirven para comparar comunas entre sí.

Limitaciones:

- La grilla pondera por superficie. Un parque o una zona sin vivienda pesa igual que una zona densa.
- La distancia en línea recta no equivale al tiempo de viaje real.
- La cobertura usa toda la red: no responde a los filtros de tipo de estación ni de servicio.

## Indicador compuesto: Acceso Relativo

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

1. Cada componente se convierte en una posición de 0 a 1 entre las 15 comunas. La comuna más baja recibe 0 y la más alta, 1. Los empates reciben el promedio de sus posiciones.
2. Acceso Relativo es el promedio de las tres posiciones, multiplicado por 100.
3. El resultado compara comunas entre sí. Una diferencia pequeña de puntaje no tiene un significado de magnitud.

Se usan posiciones y no valores mínimos y máximos porque con 15 comunas los extremos distorsionan la escala. A cambio, se pierde la magnitud de las diferencias.

El indicador usa toda la red. No responde a los filtros de tipo de estación, estructura, barrio ni servicio.

### Pesos

Los tres componentes pesan lo mismo. No existe evidencia en los datos para asignarles pesos distintos, y cualquier valor sería una decisión arbitraria. En su lugar se midió cuánto cambia el resultado si los pesos cambian.

### Sensibilidad

Se repitió el cálculo con 20.000 combinaciones de pesos al azar y quitando un componente por vez.

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

## Limitaciones

- No hay datos de demanda, de personas atendidas, de capacidad ni de horarios.
- Las estaciones móviles no necesariamente están disponibles todos los días ni todo el día.
- Presencia de una estación no equivale a uso, y disponibilidad declarada no equivale a capacidad efectiva.
- La población es del Censo 2022 y las estaciones son de 2026. No se proyectó la población.
- Las dos estaciones con campo de servicios posiblemente truncado pueden tener más servicios que los registrados. Eso afecta a las comunas 9 y 15.
- La población se asigna por comuna. Una estación atiende también a personas de otras comunas y a quienes trabajan o pasan por la zona.
- Con 15 comunas, las diferencias pequeñas entre posiciones no son estadísticamente interpretables.
