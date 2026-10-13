# Hallazgos

Estos hallazgos responden la pregunta central del proyecto: ¿la población de CABA tiene un acceso territorialmente equitativo a los servicios preventivos de las Estaciones Saludables?

Cada hallazgo separa el dato, su interpretación, por qué importa para la planificación, qué no se puede afirmar y qué conviene hacer después. Ninguno indica causalidad: describen la distribución de la oferta, no sus motivos ni sus efectos sobre la salud.

Las recomendaciones llevan una de dos marcas:

- **Respaldada por los datos.** Se desprende directamente de lo que muestran las fuentes.
- **Hipótesis a investigar.** Es una pregunta razonable que los datos disponibles no alcanzan a responder.

Los datos de estaciones son de 2026 y los de población, del Censo 2022. Los indicadores se definen en [metodologia.md](metodologia.md), y cada cifra de este documento se verifica en las pruebas automatizadas (`tests/test_proyecto.py`) o en el [informe de auditoría](QA_REPORT.md).

Este es un proyecto analítico independiente con datos públicos. No es un producto oficial del Gobierno de la Ciudad.

## 1. Hay estaciones en las 15 comunas, pero la presencia no es pareja

**Hallazgo.** Las 15 comunas tienen al menos una estación. Siete dependen de una sola y tres no tienen ninguna estación fija.

**Evidencia.**

- Comunas con una sola estación: 1, 4, 5, 9, 10, 11 y 15.
- Comunas sin estación fija, solo con móviles: 1, 10 y 13.
- Las otras ocho comunas tienen dos o tres estaciones. Las comunas 6 y 8 tienen tres.

**Interpretación.** El dato "15 de 15 comunas con presencia" describe cobertura institucional: hay un punto de la red en cada comuna. No describe cuánta oferta recibe cada una, ni qué parte de su población la tiene cerca.

**Relevancia para la planificación.** Una comuna con una sola estación no tiene alternativa si esa estación cierra, se muda o reduce sus servicios. En las comunas 1 y 10 esa única estación es además móvil.

**Limitación.** Presencia no equivale a cobertura de la población. Los datos no indican cuántas personas usan cada estación ni desde dónde llegan. Una estación atiende también a quienes viven en otras comunas, trabajan en la zona o pasan por ella.

**Recomendación.**

- *Respaldada por los datos.* Al comunicar la red, acompañar el "15 de 15" con la cantidad de estaciones por comuna, para no sugerir una cobertura uniforme.
- *Hipótesis a investigar.* Conocer si las comunas con una sola estación tienen menor uso por habitante. Requiere los datos de visitas por estación.

## 2. La cantidad de estaciones por habitante varía más de tres veces entre comunas

**Hallazgo.** La Comuna 6 tiene 1,48 estaciones cada 100.000 habitantes y la Comuna 4, 0,44.

**Evidencia.**

- La ciudad tiene 0,80 estaciones cada 100.000 habitantes: 124.868 habitantes por estación.
- La Comuna 6 tiene 67.681 habitantes por estación y la Comuna 4, 229.240. El cociente entre ambas es de 3,4.
- Las comunas 1, 4, 5, 11 y 15 están por debajo de 0,52 estaciones cada 100.000 habitantes. Las cinco tienen una sola estación.

**Interpretación.** En la Comuna 4 hay 3,4 veces más habitantes por cada estación que en la Comuna 6. Es una diferencia en la cantidad de puntos de atención respecto de la población residente.

**Relevancia para la planificación.** El indicador permite comparar comunas de distinto tamaño con una misma vara y señala dónde una estación adicional reduciría más la cantidad de habitantes por estación.

**Limitación.** El indicador cuenta estaciones, no capacidad: una estructura grande y una carpa pesan lo mismo, y no se conocen los horarios ni la dotación. Usa la población del Censo 2022 con las estaciones de 2026. Con una o dos estaciones por comuna, sumar o quitar una cambia mucho el valor.

**Recomendación.**

- *Respaldada por los datos.* Usar las estaciones por habitante, y no la sola presencia, como primer criterio para comparar comunas.
- *Hipótesis a investigar.* Verificar si las comunas con menos estaciones por habitante tienen otras ofertas preventivas cercanas (centros de salud y acción comunitaria, hospitales) que cubran la misma necesidad.

## 3. Los controles básicos están en casi todas las comunas y las prestaciones específicas, en muy pocas

**Hallazgo.** Cinco servicios llegan a 13 o 14 comunas. Cuatro servicios llegan a una o dos.

**Evidencia.**

| Servicio | Comunas que lo tienen (de 15) | Estaciones que lo ofrecen (de 24 con datos) |
|---|---|---|
| Actividad Física | 14 | 23 |
| Asesoría Nutricional, Control de Peso, Control de Presión Arterial y Control de Talla | 13 cada uno | 19 cada uno |
| Servicios de Enfermería | 12 | 18 |
| Taller Cognitivo, Talleres Literarios, Talleres de Escritura y Cumpleaños Saludables | 11 cada uno | 15 cada uno |
| Talleres para Ejercitar tu Mente | 6 | 8 |
| Control de Glucemia | 2 (comunas 5 y 9) | 2 |
| Actividades para Adultos Mayores | 2 (comunas 9 y 15) | 2 |
| Actividades para Niños (Juegotecas) y Casilleros y Cambiadores | 1 (Comuna 9) | 1 cada uno |

Estas cifras salen de toda la red, sin filtros de tipo ni de estructura. Las comunas 1 y 10 no tienen ninguno de los cuatro controles básicos.

**Interpretación.** Tener una estación en la comuna no implica que ofrezca la prestación buscada. El Control de Glucemia, por ejemplo, figura en dos de las 24 estaciones con datos.

**Relevancia para la planificación.** La brecha de disponibilidad es mayor por servicio que por estación. Para una prestación específica, el mapa relevante es el de las estaciones que la ofrecen, no el de toda la red.

**Limitación.** La cobertura se basa en lo que declara la fuente y puede estar subestimada:

- Parque Los Andes, la única estación de la Comuna 15, tiene el campo de servicios cortado. Por eso la Comuna 15 figura sin Actividad Física.
- Parque Avellaneda, la única de la Comuna 9, llega al largo máximo del campo y puede tener servicios sin registrar.
- Plaza Houssay no informa servicios y queda fuera de estos conteos.

**Recomendación.**

- *Respaldada por los datos.* Pedir al área responsable el campo de servicios completo de Parque Los Andes, Parque Avellaneda y Plaza Houssay antes de sacar conclusiones sobre las comunas 2, 9 y 15.
- *Hipótesis a investigar.* Evaluar si la baja presencia del Control de Glucemia responde a una decisión de diseño de la red o a un registro incompleto.

## 4. Las estaciones fijas ofrecen una cartera más amplia que las móviles

**Hallazgo.** Una estación fija ofrece en promedio 10,0 servicios y una móvil, 3,9.

**Evidencia.**

| Indicador | Fijas | Móviles |
|---|---|---|
| Estaciones | 17 | 8 |
| Estaciones con servicios informados | 16 | 8 |
| Servicios por estación, promedio | 10,0 | 3,9 |
| Servicios por estación, mínimo y máximo | 9 y 11 | 2 y 7 |
| Servicios diferentes | 14 de 15 | 7 de 15 |
| Comunas con presencia | 12 | 6 |

- Composición: cinco de las ocho móviles ofrecen solo dos servicios (Actividad Física y Talleres para Ejercitar tu Mente). Las otras tres ofrecen siete, que incluyen los cuatro controles básicos y Servicios de Enfermería.
- Ocho servicios figuran solo en estaciones fijas, entre ellos el Control de Glucemia y los talleres cognitivos y literarios. Uno figura solo en móviles: Talleres para Ejercitar tu Mente.

**Interpretación.** La diferencia no es solo de promedio: son dos carteras distintas. Las fijas son muy homogéneas (14 de las 16 con datos ofrecen exactamente 10 servicios) y las móviles se dividen en dos grupos.

**Relevancia para la planificación.** Contar una estación móvil como equivalente a una fija sobrestima la oferta de prestaciones en las comunas que solo tienen móviles.

**Limitación.** El promedio de las fijas excluye a Plaza Houssay, que no informa servicios; si se la contara con cero, el promedio sería 9,4. Hay solo ocho móviles, así que su promedio es sensible a cada una. Los datos no indican cuántos días ni cuántas horas funciona cada estación.

**Recomendación.**

- *Respaldada por los datos.* Informar por separado las estaciones fijas y las móviles en los indicadores de la red.
- *Hipótesis a investigar.* Averiguar si la cartera reducida de las móviles se debe a limitaciones de infraestructura o a un registro distinto del campo de servicios.

## 5. En tres comunas la única presencia es móvil y con cartera reducida

**Hallazgo.** Las comunas 1, 10 y 13 solo tienen estaciones móviles.

**Evidencia.**

- Las comunas 1 y 10 cuentan con una sola móvil de dos servicios. Su diversidad de servicios es de 13,3 % (2 de 15), la más baja de la ciudad.
- La Comuna 13 tiene dos móviles, una con siete servicios y otra con dos. Su diversidad es de 46,7 %.
- Los ocho servicios que solo figuran en estaciones fijas no están disponibles en estas tres comunas.

**Interpretación.** Las móviles extienden la presencia territorial de la red a estas comunas, pero no su cartera. Son casos de presencia con baja disponibilidad de prestaciones.

**Relevancia para la planificación.** Las tres comunas suman 660.943 habitantes, el 21 % de la población de la ciudad.

**Limitación.** Una estación móvil puede rotar de sitio, y los datos muestran una única ubicación por estación. No se sabe si los vecinos de estas comunas usan estaciones fijas de comunas vecinas.

**Recomendación.**

- *Respaldada por los datos.* Señalar estas tres comunas como casos a revisar cuando se evalúe la cartera de servicios.
- *Hipótesis a investigar.* Medir la distancia desde estas comunas a la estación fija más cercana de otra comuna, ponderada por población.

## 6. Un tercio de la superficie de la ciudad está a menos de 1.000 metros de una estación

**Hallazgo.** El 35,6 % de la superficie de la ciudad queda a 1.000 metros o menos de una estación, en línea recta.

**Evidencia.**

- A 2.000 metros, la cobertura es de 79,0 %. A 500 metros, de 9,6 %.
- La distancia media a la estación más cercana es de 1.424 metros.
- Por comuna, la cobertura a 1.000 metros va de 10,9 % (Comuna 1) a 82,3 % (Comuna 6).
- En la Comuna 9, el 37,6 % de la superficie está a menos de 2.000 metros de una estación y la distancia media es de 2.444 metros, la mayor de la ciudad.

El cálculo usa una grilla de puntos cada 50 metros y se verificó con un método geométrico independiente: las diferencias son menores que 0,5 puntos porcentuales.

**Interpretación.** La proximidad física a la red es desigual entre comunas. La cobertura de superficie y la presencia son cosas distintas: la Comuna 1 tiene una estación y solo un décimo de su superficie a menos de 1.000 metros.

**Relevancia para la planificación.** La cobertura por radio identifica zonas alejadas de la red que el conteo por comuna no muestra, y considera las estaciones de comunas vecinas.

**Limitación.** El indicador mide superficie, no personas: un parque o una zona portuaria pesan igual que una zona residencial densa. No dice cuánta población vive cerca de una estación. La distancia es en línea recta, no en tiempo de viaje, y los radios son exploratorios.

**Recomendación.**

- *Respaldada por los datos.* No presentar la cobertura de superficie como porcentaje de población cubierta.
- *Hipótesis a investigar.* Repetir el cálculo ponderando por la población de cada radio censal, para estimar la población potencialmente cercana a una estación.

## 7. El ordenamiento exploratorio de comunas es estable en los extremos y sensible en el centro

**Hallazgo.** El indicador exploratorio Acceso Relativo ubica a la Comuna 6 primera y a la Comuna 1 última en todas las variantes probadas.

**Evidencia.**

- El indicador promedia la posición de cada comuna en estaciones por habitante, cobertura de superficie a 1.000 metros y diversidad de servicios.
- Se probaron otros pesos, la exclusión de cada componente, dos normalizaciones alternativas, 20.000 combinaciones de pesos al azar y dos supuestos sobre los campos truncados. En todas, la correlación de Spearman con el ordenamiento original es de 0,92 o más.
- Grupo de menor disponibilidad relativa (comunas 1, 4, 9, 10 y 11): las comunas 1 y 4 se mantienen en el 100 % de los sorteos de pesos, la 10 en el 99 % y la 11 en el 89 %. La Comuna 9 se mantiene solo en el 54 %.
- Grupo de mayor disponibilidad relativa (comunas 2, 3, 5, 6 y 12): las comunas 6 y 2 se mantienen en el 100 % y la 3 en el 95 %. Las comunas 5 y 12, en el 64 % y el 65 %.
- El centro del ordenamiento cambia: la Comuna 8 puede ir del puesto 2 al 9.

**Interpretación.** Las comunas 1, 4, 10 y 11 aparecen con menor disponibilidad relativa cualquiera sea el criterio razonable que se use. La ubicación de la Comuna 9 depende de los pesos y de un dato posiblemente incompleto: con un servicio más en Parque Avellaneda pasaría al grupo intermedio.

**Relevancia para la planificación.** El indicador sirve para ordenar por dónde empezar un análisis más detallado. No sirve para asignar recursos ni para comparar magnitudes: un puntaje del doble no significa el doble de oferta.

**Limitación.**

- Compara comunas entre sí y no mide el acceso efectivo de las personas. No incorpora demanda, uso, horarios ni capacidad.
- Las estaciones por habitante son uno de sus tres componentes. Que el grupo de menor disponibilidad tenga 5 estaciones para 999.462 habitantes y el de mayor tenga 10 para 992.086 es, en parte, consecuencia de cómo se arman los grupos.
- La diversidad tiene solo cuatro valores distintos entre las 15 comunas, y el método de posiciones amplifica la diferencia de un solo servicio.
- No es evidencia causal de inequidad sanitaria.

**Recomendación.**

- *Respaldada por los datos.* Comenzar el análisis de detalle por las comunas 1, 4, 10 y 11.
- *Respaldada por los datos.* Completar el dato de servicios de Parque Avellaneda antes de clasificar a la Comuna 9.
- *Hipótesis a investigar.* Contrastar el ordenamiento con datos de uso (visitas por estación) y de necesidad (población mayor, indicadores de salud por comuna).

## Qué no se puede afirmar

- Que la población de una comuna con baja disponibilidad relativa tenga peor acceso efectivo a la prevención.
- Que una comuna con baja disponibilidad tenga una necesidad mayor de servicios.
- Que las diferencias se deban a decisiones de política y no a la historia de cada espacio público.
- Que la población use la estación más cercana a su casa.
- Que los servicios funcionen todos los días: los datos no traen días ni horarios.
- Que la cobertura de superficie equivalga a población cubierta.

## Conclusión

La red de Estaciones Saludables está presente en las 15 comunas, pero con diferencias medibles en tres aspectos de la oferta: la cantidad de estaciones respecto de la población (de 0,44 a 1,48 cada 100.000 habitantes), la cartera de servicios (10,0 en promedio en las fijas y 3,9 en las móviles) y la superficie cercana a una estación (de 10,9 % a 82,3 % a 1.000 metros).

Con los datos disponibles se puede describir la distribución territorial de la oferta declarada. No se puede concluir que el acceso sea equitativo ni que no lo sea: para eso harían falta datos de demanda, uso, capacidad, horarios y tiempos de viaje.
