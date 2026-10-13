# Proyecto: Acceso a Servicios de Salud Preventiva en CABA

## 1. Objetivo general

Desarrollar un proyecto de análisis de datos y Power BI orientado a estudiar la **accesibilidad territorial a servicios de prevención y promoción de la salud en la Ciudad Autónoma de Buenos Aires**, utilizando como punto de partida la red de Estaciones Saludables.

El proyecto no debe limitarse a mostrar la ubicación de las estaciones.

El objetivo analítico es responder:

> **¿Qué tan accesibles son los servicios preventivos de salud según la ubicación, disponibilidad de prestaciones, infraestructura y población de cada territorio de CABA?**

El resultado final deberá ser apto para incorporarse a un portfolio profesional de Data Analytics / Business Intelligence especializado en salud.

---

# 2. Fuentes disponibles

Actualmente existen dos archivos:

```text
estaciones_saludables.csv
estaciones_saludables.geo.json
```

Ambos representan esencialmente el mismo universo de Estaciones Saludables.

El GeoJSON contiene adicionalmente la geometría de cada establecimiento como coordenadas geográficas.

No duplicar los registros cargando ambas fuentes como tablas de hechos independientes.

Utilizar ambas solamente cuando sea necesario para obtener o validar información.

---

# 3. Universo actual

La fuente contiene:

```text
25 Estaciones Saludables
17 Fijas
8 Móviles
15 comunas representadas
```

Distribución de infraestructura identificada:

```text
12 Estructuras Grandes
4 Estructuras Medianas
7 Carpas
2 Sin Información
```

La existencia de estaciones en las 15 comunas **no debe interpretarse automáticamente como acceso equitativo**.

El objetivo será analizar posteriormente la cobertura relativa considerando población, superficie, distancia y servicios disponibles.

---

# 4. Etapa 1 — Auditoría de datos

Antes de transformar cualquier información realizar un perfilado de ambos archivos.

Validar:

- cantidad de registros;
- IDs únicos;
- duplicados;
- valores nulos;
- consistencia entre CSV y GeoJSON;
- diferencias entre registros;
- nombres de estaciones;
- barrios;
- comunas;
- tipo;
- estructura;
- servicios;
- coordenadas;
- posibles valores truncados;
- posibles errores de codificación;
- coordenadas fuera de rango.

Generar un pequeño informe QA con:

```text
Registros CSV
Registros GeoJSON
IDs coincidentes
IDs faltantes
Duplicados
Nulos por campo
Problemas detectados
```

No modificar silenciosamente datos dudosos.

Todo problema de calidad deberá quedar documentado.

---

# 5. Problemas de calidad ya identificados

## Plaza Houssay

La estación:

```text
Estación Saludable Plaza Houssay
```

posee:

```text
servicio = null
```

No asumir automáticamente que no ofrece servicios.

Clasificar inicialmente como:

```text
Información de servicios no disponible
```

---

## Parque Los Andes

El campo `servicio` termina con:

```text
Actividade
```

Esto podría indicar truncamiento del campo original.

No completar arbitrariamente el texto.

Crear un flag:

```text
Flag_Calidad_Servicio
```

Ejemplo:

```text
OK
SERVICIO_NULL
POSIBLE_TRUNCAMIENTO
```

Investigar la fuente original únicamente si es posible hacerlo de forma confiable.

---

# 6. Tabla principal de estaciones

Crear una tabla limpia:

```text
Dim_Estacion
```

Campos esperados:

```text
id_estacion
nombre
tipo
estructura
direccion
barrio
comuna
numero_comuna
latitud
longitud
cantidad_servicios
flag_calidad
```

Normalizaciones:

- eliminar espacios innecesarios;
- estandarizar mayúsculas/minúsculas;
- mantener nombres oficiales;
- extraer número de comuna;
- convertir coordenadas a decimal;
- validar latitud y longitud;
- evitar duplicados por `id_estacion`.

---

# 7. Coordenadas

Del GeoJSON utilizar:

```text
geometry.coordinates[0] = longitud
geometry.coordinates[1] = latitud
```

Crear:

```text
Latitud
Longitud
```

como columnas numéricas decimales.

Validar que todos los puntos se encuentren geográficamente dentro de CABA.

---

# 8. Normalización de servicios

Actualmente los servicios aparecen concatenados en una única columna.

Ejemplo:

```text
Asesoría Nutricional - Control de Peso - Control de Presión Arterial - Control de Talla - Actividad Física
```

Esto no debe permanecer como estructura analítica final.

Separar la información para obtener una relación:

```text
Estación ↔ Servicio
```

Crear:

```text
Bridge_Estacion_Servicio
```

con estructura:

```text
id_estacion
id_servicio
servicio
```

Ejemplo:

```text
3 | 01 | Asesoría Nutricional
3 | 02 | Control de Peso
3 | 03 | Control de Presión Arterial
3 | 04 | Control de Talla
3 | 05 | Actividad Física
```

Cada fila debe representar:

> Una estación ofreciendo un servicio.

No generar registros para servicios desconocidos o nulos.

---

# 9. Dimensión de servicios

Crear:

```text
Dim_Servicio
```

Campos:

```text
id_servicio
servicio
categoria_servicio
```

Inicialmente `categoria_servicio` puede quedar sin asignar si no existe una clasificación objetiva.

Posteriormente podría utilizarse una clasificación como:

```text
Controles preventivos
Enfermería
Nutrición
Actividad física
Salud cognitiva
Actividades comunitarias
Infraestructura / apoyo
```

Pero no inventar categorías sin documentar el criterio.

---

# 10. Modelo dimensional inicial

Construir:

```text
Dim_Estacion
      1
      │
      │
      ∞
Bridge_Estacion_Servicio
      ∞
      │
      │
      1
Dim_Servicio
```

Dirección de filtro preferentemente simple desde las dimensiones hacia la bridge.

Evitar relaciones bidireccionales salvo necesidad justificada.

---

# 11. Métricas descriptivas iniciales

Calcular como mínimo:

```text
Cantidad Estaciones
Cantidad Estaciones Fijas
Cantidad Estaciones Móviles
Cantidad Comunas con Estaciones
Cantidad Barrios con Estaciones
Cantidad Servicios Diferentes
Cantidad Relaciones Estación-Servicio
Promedio Servicios por Estación
```

También:

```text
Estaciones por Comuna
Estaciones por Barrio
Estaciones por Tipo
Estaciones por Estructura
Servicios por Estación
Servicios por Comuna
```

---

# 12. Disponibilidad de servicios

Analizar para cada servicio:

```text
Cantidad de estaciones que lo ofrecen
Cantidad de comunas donde está disponible
% de estaciones que lo ofrecen
% de comunas donde está disponible
```

Crear métricas:

```text
Estaciones con Servicio
Comunas con Servicio
Cobertura Comunas %
Cobertura Estaciones %
```

Ejemplo conceptual:

```text
Actividad Física
15 / 15 comunas

Control de Glucemia
2 / 15 comunas
```

Esto deberá permitir detectar servicios con alta y baja disponibilidad territorial.

---

# 13. Diversidad de servicios

Crear una métrica:

```text
Cantidad Servicios por Estación
```

y otra:

```text
Cantidad Servicios Diferentes por Comuna
```

Posteriormente evaluar un indicador de diversidad:

```text
Diversidad Servicios =
Cantidad servicios disponibles en la comuna
/
Cantidad total de servicios posibles
```

El valor deberá estar entre:

```text
0 y 1
```

o expresarse como porcentaje.

---

# 14. Diferencia entre estaciones fijas y móviles

Comparar:

```text
Fija
vs
Móvil
```

respecto de:

- cantidad promedio de servicios;
- diversidad de servicios;
- infraestructura;
- distribución geográfica;
- cobertura territorial.

En el dataset inicial parece existir una diferencia importante entre la cantidad de servicios disponibles en estaciones fijas y móviles.

Verificarla analíticamente.

No utilizar valores precalculados sin recalcularlos directamente desde los archivos.

---

# 15. Concepto de acceso

El proyecto deberá estudiar el acceso desde tres dimensiones.

---

## 15.1 Acceso físico

Responder:

> ¿Existe una estación razonablemente cercana para la población?

Indicadores futuros:

```text
Cantidad de estaciones
Estaciones por km²
Distancia a estación más cercana
Cobertura por radio
```

Radios exploratorios posibles:

```text
0 – 500 m
500 – 1.000 m
1.000 – 2.000 m
> 2.000 m
```

Estos rangos deberán considerarse exploratorios hasta justificar metodológicamente su uso.

---

## 15.2 Acceso a servicios

Responder:

> ¿La estación cercana realmente ofrece el servicio que necesita la persona?

Ejemplo:

Una comuna puede tener varias estaciones, pero ninguna ofrecer determinados controles preventivos.

Analizar:

```text
Servicio
Estaciones que lo ofrecen
Comunas donde existe
Estaciones por comuna
Cobertura territorial
```

---

## 15.3 Acceso poblacional

Responder:

> ¿La cantidad y diversidad de servicios es adecuada respecto de la población potencialmente atendida?

Para esto será necesario incorporar nuevas fuentes.

---

# 16. Datos externos necesarios

Buscar preferentemente fuentes oficiales del Gobierno de la Ciudad de Buenos Aires, INDEC u organismos públicos.

Prioridad:

## Obligatorio

```text
Población por comuna
Superficie por comuna
```

## Muy recomendable

```text
Población por edad
Población adulta mayor
Densidad poblacional
```

## Ideal

```text
Datos por radio censal
Polígonos geográficos de comunas
Polígonos de radios censales
```

Registrar siempre:

```text
fuente
URL
fecha de consulta
año de referencia
nivel geográfico
metodología
```

No mezclar años sin documentarlo.

---

# 17. Dimensión territorial

Crear:

```text
Dim_Comuna
```

Campos esperados:

```text
id_comuna
comuna
poblacion
superficie_km2
densidad_poblacional
poblacion_adulta_mayor
```

En caso de disponer de datos suficientes.

Modelo futuro:

```text
Dim_Comuna
     1
     │
     ∞
Dim_Estacion
```

Evaluar correctamente la dirección de filtro y evitar relaciones ambiguas.

---

# 18. Indicadores normalizados

Una vez incorporada población:

```text
Estaciones cada 100.000 habitantes =
DIVIDE(
    [Cantidad Estaciones],
    [Poblacion]
) * 100000
```

Crear además:

```text
Estaciones Fijas cada 100.000 habitantes
Estaciones Móviles cada 100.000 habitantes
Servicios cada 100.000 habitantes
```

Considerar también:

```text
Estaciones por km²
Habitantes por Estación
```

Estos indicadores deberán permitir comparar comunas con tamaños poblacionales diferentes.

---

# 19. Índice de Acceso a Servicios

No crear inicialmente un índice arbitrario.

Primero evaluar qué variables están disponibles y justificar metodológicamente cada componente.

Conceptualmente podría contener:

```text
Proximidad
Disponibilidad de servicios
Diversidad de servicios
Infraestructura
Estaciones por población
```

Ejemplo conceptual solamente:

```text
IAS =
    proximidad
  + disponibilidad
  + infraestructura
  + cobertura poblacional
```

Si se utilizan pesos, documentar:

- por qué se eligieron;
- cómo fueron normalizadas las variables;
- sensibilidad del resultado a cambios de pesos.

No utilizar valores como `35%`, `30%`, etc. sin justificación metodológica.

---

# 20. Power BI — Página 1

# Acceso Territorial

Objetivo:

> Mostrar la distribución geográfica general de la red de Estaciones Saludables.

KPIs:

```text
25
Estaciones

17
Fijas

8
Móviles

15 / 15
Comunas con presencia
```

Los valores deben ser medidas dinámicas y no texto hardcodeado.

Visual principal:

```text
Mapa de CABA
```

Mostrar:

```text
Estaciones Fijas
Estaciones Móviles
```

Tooltip esperado:

```text
Nombre
Tipo
Estructura
Dirección
Barrio
Comuna
Cantidad Servicios
```

Filtros:

```text
Comuna
Barrio
Tipo
Estructura
Servicio
```

Agregar visuales complementarios para:

```text
Estaciones por Comuna
Distribución por Tipo
Distribución por Estructura
```

---

# 21. Power BI — Página 2

# Disponibilidad de Servicios

Objetivo:

> Identificar qué prestaciones están disponibles y dónde existen brechas.

KPIs:

```text
Servicios Diferentes
Promedio Servicios por Estación
Servicio más disponible
Servicio menos disponible
```

Crear matriz:

```text
Servicio × Comuna
```

Representar disponibilidad mediante:

```text
Sí / No
```

o formato condicional.

Ejemplo:

```text
                         C1 C2 C3 C4 ... C15

Actividad Física          ●  ●  ●  ●       ●
Asesoría Nutricional      ○  ●  ●  ●       ●
Presión Arterial          ○  ●  ●  ●       ●
Glucemia                  -  -  -  -       -
```

Agregar ranking:

```text
Servicios con mayor disponibilidad
Servicios con menor disponibilidad
```

Crear visual:

```text
Cobertura territorial por servicio
```

utilizando:

```text
Comunas con Servicio
/
15
```

---

# 22. Power BI — Página 3

# Brechas de Acceso

Esta será la página analítica principal una vez incorporada población.

Objetivo:

> Detectar comunas potencialmente subatendidas respecto de su población.

Incluir:

```text
Población
Estaciones
Estaciones / 100k habitantes
Habitantes por estación
Servicios disponibles
Servicios / 100k habitantes
Diversidad de servicios
Estaciones fijas
Estaciones móviles
```

Visual recomendado:

```text
Scatter Plot
```

Ejemplo:

```text
X = población

Y = estaciones cada 100.000 habitantes

Tamaño = cantidad de servicios

Leyenda = comuna
```

Evaluar otras combinaciones si cuentan mejor la historia.

---

# 23. Mapa de brechas

Crear un mapa coroplético por comuna una vez obtenidos los polígonos geográficos.

Variable principal:

```text
Acceso relativo
```

o alguno de los indicadores normalizados.

Ejemplo conceptual:

```text
menor acceso relativo
↓
Comuna
↓
mayor acceso relativo
```

No utilizar colores como bueno/malo si el indicador no permite afirmarlo objetivamente.

Preferir etiquetas:

```text
Mayor disponibilidad relativa
Menor disponibilidad relativa
```

---

# 24. Storytelling

El dashboard no debe limitarse a responder:

> ¿Cuántas estaciones hay?

Debe permitir responder:

1. ¿Dónde están?
2. ¿Qué servicios ofrecen?
3. ¿Existen comunas con poca oferta?
4. ¿Qué servicios tienen menor cobertura territorial?
5. ¿Las estaciones móviles compensan brechas territoriales?
6. ¿Las estaciones fijas ofrecen una cartera de servicios más amplia?
7. ¿Qué comunas tienen menor cantidad de estaciones respecto de su población?
8. ¿Dónde existe presencia territorial pero baja disponibilidad de prestaciones?
9. ¿Qué territorios deberían analizarse prioritariamente?

---

# 25. Diseño

Crear un dashboard moderno, profesional y orientado a portfolio.

Principios:

```text
minimalista
buena jerarquía visual
pocos colores
alto contraste
tipografía limpia
espaciado consistente
sin sobrecarga de gráficos
```

El mapa debe funcionar como componente principal de navegación.

No llenar cada página de visuales.

Preferir:

```text
1 visual protagonista
2-4 visuales secundarios
KPIs
filtros relevantes
```

---

# 26. DAX

Todas las métricas importantes deberán construirse como medidas.

Crear una carpeta de medidas:

```text
_Medidas
```

Organizarlas mediante Display Folders:

```text
01 - Estaciones
02 - Servicios
03 - Territorio
04 - Población
05 - Acceso
06 - QA
```

Usar:

```text
DIVIDE()
```

cuando exista riesgo de división por cero.

Evitar columnas calculadas cuando Power Query o el modelo puedan resolver el problema mejor.

Documentar las medidas importantes.

---

# 27. Power Query

Realizar las transformaciones ETL preferentemente en Power Query:

```text
CSV / GeoJSON
        ↓
limpieza
        ↓
normalización
        ↓
Dim_Estacion
        ↓
Bridge_Estacion_Servicio
        ↓
Dim_Servicio
```

Crear nombres de queries claros.

Ejemplo:

```text
00_SRC_Estaciones_CSV
00_SRC_Estaciones_GeoJSON

01_STG_Estaciones

02_DIM_Estacion
02_DIM_Servicio
02_BRIDGE_EstacionServicio
```

Si se agregan datos poblacionales:

```text
00_SRC_Poblacion
01_STG_Poblacion
02_DIM_Comuna
```

Deshabilitar carga de queries intermedias cuando corresponda.

---

# 28. QA del modelo

Validar:

```text
Dim_Estacion[id_estacion]
```

debe ser única.

Validar:

```text
Dim_Servicio[id_servicio]
```

debe ser única.

En:

```text
Bridge_Estacion_Servicio
```

la combinación:

```text
id_estacion + id_servicio
```

no debe duplicarse.

Verificar:

- relaciones;
- cardinalidad;
- dirección de filtros;
- IDs huérfanos;
- servicios duplicados por diferencias de texto;
- comunas inconsistentes;
- coordenadas;
- registros nulos.

---

# 29. QA del dashboard

Antes de finalizar verificar:

### Datos

- Totales correctos.
- Filtros consistentes.
- No doble conteo.
- Medidas validadas manualmente.

### Modelo

- Esquema limpio.
- Relaciones sin ambigüedad.
- No utilizar relaciones bidireccionales innecesarias.
- Ocultar claves técnicas al usuario.

### Visuales

- títulos claros;
- unidades claras;
- tooltips;
- formatos numéricos;
- ausencia de visuales redundantes;
- filtros funcionando;
- interacciones coherentes.

### Geografía

- coordenadas correctas;
- estaciones correctamente ubicadas;
- comunas correctamente relacionadas.

---

# 30. Insights

Una vez finalizado el modelo, generar automáticamente una sección de conclusiones.

Separar claramente:

```text
Hallazgo
Evidencia
Interpretación
Limitación
```

Ejemplo:

```text
Hallazgo:
El servicio X presenta baja disponibilidad territorial.

Evidencia:
Está disponible únicamente en X de las 15 comunas.

Interpretación:
La presencia física de una Estación Saludable no garantiza acceso homogéneo a esta prestación.

Limitación:
El dataset no contiene información de capacidad, horarios ni cantidad de personas atendidas.
```

No inferir causalidad únicamente a partir de distribución geográfica.

---

# 31. Limitaciones del análisis

Documentar como mínimo:

- No existe información de demanda.
- No existe información de cantidad de pacientes atendidos.
- No conocemos capacidad operativa.
- No conocemos horarios.
- No conocemos dotación profesional.
- No sabemos si todas las prestaciones funcionan todos los días.
- Presencia física no equivale a utilización.
- Disponibilidad declarada no equivale a capacidad efectiva.
- Una estación móvil no necesariamente tiene la misma disponibilidad temporal que una fija.
- La proximidad geográfica no representa necesariamente tiempo real de viaje.
- Los datos poblacionales pueden corresponder a períodos distintos de los datos de estaciones.

---

# 32. Posibles extensiones futuras

Dejar preparada la arquitectura para incorporar:

```text
Centros de Salud
CeSAC
Hospitales
Centros Médicos Barriales
Vacunatorios
Farmacias
Centros de diagnóstico
```

El modelo podría evolucionar desde:

```text
Estaciones Saludables
```

hacia:

```text
Accesibilidad territorial al sistema de salud
```

---

# 33. Estructura esperada del repositorio

Organizar el proyecto de forma profesional.

```text
acceso-servicios-salud-caba/
│
├── README.md
│
├── LICENSE
│
├── .gitignore
│
├── data/
│   ├── raw/
│   │   ├── estaciones_saludables.csv
│   │   └── estaciones_saludables.geo.json
│   │
│   ├── external/
│   │   ├── poblacion_comunas.*
│   │   └── comunas_geo.*
│   │
│   └── processed/
│
├── powerbi/
│   └── acceso-servicios-salud-caba.pbip
│
├── docs/
│   ├── metodologia.md
│   ├── fuentes.md
│   ├── modelo-datos.md
│   └── qa.md
│
├── images/
│   ├── portada.png
│   ├── acceso-territorial.png
│   ├── servicios.png
│   └── brechas.png
│
└── scripts/
```

No subir información temporal innecesaria generada por Power BI.

---

# 34. README final

El README deberá explicar el proyecto desde una perspectiva analítica, no solamente tecnológica.

Introducción propuesta:

> **Acceso a Servicios de Salud Preventiva en CABA**
>
> Este proyecto analiza la accesibilidad territorial a servicios de prevención y promoción de la salud en la Ciudad Autónoma de Buenos Aires.
>
> Se integran datos geoespaciales de Estaciones Saludables con información sobre servicios, infraestructura y características territoriales para detectar diferencias en la disponibilidad de prestaciones entre comunas.
>
> El objetivo no es únicamente identificar dónde existen establecimientos, sino analizar si su distribución y cartera de servicios ofrecen una cobertura territorial homogénea respecto de la población.

Después incluir:

```text
Objetivo
Preguntas de negocio
Fuentes
Metodología
Modelo de datos
KPIs
Dashboard
Principales hallazgos
Limitaciones
Stack tecnológico
Estructura del repositorio
```

---

# 35. Stack tecnológico

Documentar:

```text
Power BI
Power Query
DAX
PBIP
TMDL
PBIR
Git
GitHub
GeoJSON
```

Agregar Python o SQL únicamente si efectivamente son utilizados.

---

# 36. Forma de trabajo

No desarrollar todo directamente sin validaciones intermedias.

Trabajar por etapas:

```text
FASE 1
Auditoría y QA de fuentes

FASE 2
ETL y normalización

FASE 3
Modelo dimensional

FASE 4
Métricas descriptivas

FASE 5
Análisis de servicios

FASE 6
Incorporación de población y geografía

FASE 7
Indicadores de acceso

FASE 8
Diseño Power BI

FASE 9
QA técnico y visual

FASE 10
Insights y documentación

FASE 11
Preparación para GitHub
```

Al terminar cada fase:

1. resumir lo realizado;
2. informar problemas encontrados;
3. validar resultados;
4. continuar con la siguiente fase solamente cuando no existan errores bloqueantes.

---

# 37. Uso de agentes / skills de Power BI

Si el entorno dispone del repositorio:

```text
data-goblin/power-bi-agentic-development
```

utilizar sus skills especializadas cuando aporten valor.

Especialmente:

```text
PBIP
Semantic Model
DAX
Power Query
Report Design
Report Creation
Power BI Desktop
Report Review
PBIP Validation
```

No utilizar agentes innecesarios únicamente porque estén disponibles.

Aplicar principio:

> El agente especializado construye; otro mecanismo independiente valida.

Siempre realizar QA posterior a cambios automáticos.

---

# 38. Resultado final esperado

El proyecto debe terminar con:

```text
✓ Datos limpios
✓ Modelo dimensional
✓ Servicios normalizados
✓ Datos geográficos
✓ Datos poblacionales
✓ KPIs
✓ Indicadores de acceso
✓ Dashboard Power BI
✓ 3 páginas principales
✓ QA técnico
✓ QA visual
✓ Insights
✓ Metodología
✓ Documentación
✓ README
✓ Proyecto PBIP versionable
✓ Repositorio GitHub listo para portfolio
```

El producto final debe demostrar simultáneamente:

```text
Business Intelligence
Data Analysis
Healthcare Analytics
Data Modeling
ETL
DAX
Data Visualization
Geospatial Analysis
Data Quality
Storytelling
Git / Version Control
AI-assisted development
```

---

# 39. Criterio principal del proyecto

La pregunta central que debe guiar todas las decisiones es:

> **¿La población de CABA tiene un acceso territorialmente equitativo a los servicios preventivos disponibles en las Estaciones Saludables?**

No confundir:

```text
tener una estación
```

con:

```text
tener acceso efectivo a servicios.
```

La presencia de infraestructura será tratada como una dimensión del acceso, no como evidencia suficiente de cobertura sanitaria.