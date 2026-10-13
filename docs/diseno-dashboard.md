# Diseño del dashboard

El dashboard tiene tres páginas de 1920 por 1080 píxeles. Cada una responde una parte de la pregunta central: ¿la población de CABA tiene un acceso territorialmente equitativo a los servicios preventivos de las Estaciones Saludables?

## Principios

- Un visual protagonista por página, entre dos y cuatro visuales secundarios, tarjetas de indicadores y filtros relevantes.
- Pocos colores, alto contraste y tipografía limpia.
- Las tarjetas son medidas, no texto fijo.
- Ningún color significa "bueno" o "malo". Las etiquetas describen una posición relativa.

## Sistema visual

| Elemento | Decisión |
|---|---|
| Fondo de página | Gris muy claro (`#F3F4F6`) |
| Fondo de visuales | Blanco, borde fino gris y esquinas redondeadas |
| Texto | Azul noche (`#0A2A3C`) para valores y títulos, gris (`#4A4F55`) para etiquetas y gris verdoso (`#5F6B6D`) para notas |
| Estaciones fijas | Azul noche `#0A2A3C`, el color de la portada del manual de estilo |
| Estaciones móviles | Verde agua oscurecido `#2F8F8A`, derivado del `#79C7C3` del manual |
| Acceso Relativo | Tres tonos para los grupos de comunas: azul noche `#0A2A3C`, azul `#4B8DDC` y celeste `#86DCE5`. El degradado de la dispersión va del celeste al azul noche |
| Tipografía | Archivo, la del tema. Valores de tarjetas en 40 puntos, títulos en 14, texto de tablas entre 11 y 13 |
| Retícula | Márgenes de 40 píxeles y separación de 20 entre visuales |

Los colores salen del tema "CABA Salud Preventiva" (`StaticResources/RegisteredResources`) y del Manual de estilo del Gobierno de la Ciudad (resolución PE-RES-SECLYT-SECLYT-280-25, anexo; no se incluye en el repositorio), que no define una paleta de datos pero sí usa un azul noche (`#0A2A3C`), un azul oscuro (`#143244`), un verde agua (`#79C7C3`) y un amarillo (`#FECB04`) en su diseño. Las fijas llevan el azul noche del manual y las móviles un verde agua oscurecido, porque el `#79C7C3` original es muy claro sobre fondo blanco. El par pasó la separación para daltonismo (32,4 contra un objetivo de 8), la separación para visión normal (32,9 contra un piso de 15) y el contraste contra la superficie. No pasa dos controles del verificador, la banda de luminosidad y el piso de saturación, porque el azul noche es casi negro y el verde agua oscurecido tiene poca saturación; la diferencia de claridad entre ambos es grande y compensa. El amarillo del tema (`#F2C300`) no pasa el contraste y quedó afuera de los datos.

El tema se importó desde Power BI Desktop. Los colores de los visuales no usan los predeterminados: se fijaron con los mismos valores del tema, y el fondo, el borde y el título de cada visual están definidos en el propio visual.

## Páginas

### 1. Acceso Territorial

Responde dónde están las estaciones y qué infraestructura tienen.

| Zona | Contenido |
|---|---|
| Tarjetas | Estaciones, fijas, móviles y comunas con presencia ("15 / 15") |
| Filtros | Comuna, barrio, tipo, estructura y servicio |
| Visual principal | Mapa de ArcGIS con las estaciones por latitud y longitud, color por tipo. El tooltip muestra nombre, tipo, estructura, dirección, comuna y cantidad de servicios |
| Secundarios | Estaciones por comuna, distribución por tipo y distribución por estructura |

### 2. Disponibilidad de Servicios

Responde qué prestaciones hay en cada comuna y dónde existen brechas.

| Zona | Contenido |
|---|---|
| Tarjetas | Servicios diferentes, promedio de servicios por estación, servicio más disponible y menos disponible |
| Filtros | Tipo, estructura y comuna |
| Visual principal | Matriz de servicio por comuna: círculo lleno si hay una estación que lo ofrece y círculo vacío si no. Los servicios se ordenan del más al menos disponible |
| Secundarios | Cobertura territorial por servicio (comunas con el servicio sobre 15) y una tabla que compara fijas y móviles |

### 3. Brechas de Acceso

Responde qué comunas tienen menor disponibilidad relativa respecto de su población.

| Zona | Contenido |
|---|---|
| Tarjetas | Población, estaciones, estaciones cada 100.000 habitantes y habitantes por estación |
| Filtro | Tipo de estación, para comparar fijas y móviles |
| Visual principal | Mapa de ArcGIS con un círculo en el centro de cada comuna: color por grupo de Acceso Relativo y tamaño por población |
| Secundarios | Dispersión de población contra estaciones cada 100.000 habitantes (color por Acceso Relativo y tamaño por servicios) y una tabla con todos los indicadores por comuna |
| Nota | Texto breve que explica qué mide el Acceso Relativo y sus límites |

## Cómo responde el dashboard a las preguntas del proyecto

| Pregunta | Dónde se ve |
|---|---|
| 1. ¿Dónde están? | Página 1, mapa |
| 2. ¿Qué servicios ofrecen? | Página 2, matriz |
| 3. ¿Hay comunas con poca oferta? | Página 3, mapa y tabla |
| 4. ¿Qué servicios tienen menor cobertura territorial? | Página 2, cobertura territorial por servicio |
| 5. ¿Las móviles compensan brechas? | Página 2, tabla de fijas y móviles. Página 3, filtro de tipo |
| 6. ¿Las fijas ofrecen una cartera más amplia? | Página 2, tabla de fijas y móviles |
| 7. ¿Qué comunas tienen menos estaciones respecto de su población? | Página 3, dispersión y tabla |
| 8. ¿Dónde hay presencia pero baja disponibilidad de prestaciones? | Página 3, columnas de estaciones y diversidad de la tabla, y matriz de la página 2 |
| 9. ¿Qué territorios analizar primero? | Página 3, mapa de Acceso Relativo y tabla ordenada |

## Interacción

- Los filtros y la selección en un visual afectan a los demás de la página.
- El mapa de estaciones responde al filtro de servicio: solo muestra las estaciones que lo ofrecen.
- El mapa de comunas y el Acceso Relativo usan siempre toda la red y no responden a los filtros de tipo ni de servicio.
- El barrio no está en el mapa de estaciones, pero sí como filtro de la página.

## Accesibilidad

- Todos los visuales tienen texto alternativo.
- La matriz no depende del color: el círculo lleno o vacío lleva la información, y el color la refuerza.
- El mapa de estaciones tiene leyenda. Los tamaños de texto son de 11 puntos o más.
- El Acceso Relativo usa un solo tono de claro a oscuro, que no depende de distinguir matices.

## Qué se verificó y qué no

Verificado:

- Los archivos del reporte cumplen los esquemas oficiales de Microsoft: 47 visuales, 3 páginas y la configuración general.
- Los 103 campos y medidas que usan los visuales existen en el modelo, y ningún visual repite un campo.
- Los datos que reciben los dos mapas coinciden con el cálculo independiente: 25 estaciones con sus campos y 15 comunas con coordenadas, grupo, población y puntaje.
- Las consultas de la matriz devuelven 15 comunas y 15 servicios, y el mapa de estaciones queda en 2 puntos con el filtro de Control de Glucemia.

No verificado:

- **El aspecto de las páginas.** No se pudo ver el reporte renderizado. Falta revisar solapamientos, cortes de texto y proporciones.
- **Los símbolos de los mapas de ArcGIS.** Se escribieron a mano sobre el formato que guardó Desktop. Si no se ven como se describe, se ajustan desde el panel de formato del visual.
- El color por Acceso Relativo en la dispersión y el color de los símbolos de la matriz.

## Decisión: círculos en lugar de polígonos

El mapa de comunas es de círculos y no de polígonos coloreados. Los mapas nativos de Power BI no dibujaron los polígonos de las comunas en las pruebas, y ArcGIS no reconoce las comunas por su nombre sin una capa de límites propia. El círculo se ubica en el centro de la comuna, o en un punto interior si el centro cae fuera del polígono.

Si más adelante se publica una capa de límites de comunas en ArcGIS, el mapa puede pasar a polígonos sin cambiar las medidas.

## Versión en HTML

[`index.html`](../index.html) reproduce las tres páginas del informe en un solo archivo. Se genera con [construir_dashboard_html.py](../scripts/construir_dashboard_html.py), que lee los archivos de origen, calcula los indicadores y arma el mapa en SVG a partir de los polígonos de comunas. La plantilla está en [plantilla_dashboard.html](../scripts/plantilla_dashboard.html).

Qué comparte con el informe de Power BI:

- La portada, la paleta del tema "CABA Salud Preventiva" y la tipografía Archivo.
- Las mismas tres secciones, con sus tarjetas, filtros, matriz de servicios, cobertura territorial por servicio, comparación de fijas y móviles, dispersión y tabla de indicadores.
- Las mismas reglas de cálculo: el indicador compuesto y el mapa de comunas usan siempre toda la red, y los demás indicadores responden a los filtros.

Qué hace distinto:

- El mapa de comunas se dibuja como polígonos coloreados por Acceso Relativo, con escala continua, porque el HTML no depende de un servicio de mapas.
- Agrega un panel de preguntas rápidas con las respuestas del proyecto y soporte para tema claro y oscuro.
- No usa librerías externas: los gráficos son SVG y HTML propios. Solo carga la tipografía desde Google Fonts.

### Accesibilidad y rendimiento del HTML

- Enlace para saltar al contenido, foco visible, puntos y comunas de los mapas accesibles con teclado y con etiqueta, y nombre accesible en las tres tablas.
- La etiqueta del grupo intermedio usa el azul `#2172D4` del tema con texto blanco (contraste de 4,8 a 1). El tono anterior daba 3,3 a 1 y no alcanzaba el mínimo de 4,5.
- En pantallas de menos de 760 píxeles, la barra de navegación ocupa una sola fila con desplazamiento horizontal. Antes ocupaba cuatro filas y, al quedar fija, tapaba un cuarto de la pantalla.
- La tipografía se carga sin bloquear el primer dibujado de la página, y el ícono va incrustado para no pedir un archivo que no existe.
- El encabezado y el pie aclaran que es un proyecto analítico independiente y no un producto oficial.

Las mediciones de Lighthouse de antes y después están en [QA_REPORT.md](QA_REPORT.md).

### Color en el HTML

| Uso | Claro | Oscuro |
|---|---|---|
| Estaciones fijas | `#0A2A3C` | `#86DCE5` |
| Estaciones móviles | `#2F8F8A` | `#2F8F8A` |
| Escala de Acceso Relativo | `#DCEFF4`, `#4B8DDC`, `#0A2A3C` | `#1B4D5C`, `#3599B8`, `#A4DDEE` |
| Texto y encabezados | `#0A2A3C` | `#EAF1F5` |
| Acento | `#F2C300`, solo como detalle gráfico | `#F2C300` |

Los colores salen de la paleta del tema y del manual. Con el verificador de la habilidad de visualización, el par de fijas y móviles pasa la separación para daltonismo (32,4 en claro y 24,9 en oscuro, contra un objetivo de 8) y el contraste mínimo contra la superficie. Falla la banda de luminosidad y el piso de saturación, por el mismo motivo que en Power BI. El amarillo `#F2C300` quedó afuera de los datos porque no pasa el contraste (1,6 contra 3 necesarios) y se usa solo como línea decorativa, igual que en la portada.
