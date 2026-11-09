# MAPA SOCIALTECH — Plan maestro del proyecto

> **Estado:** plan aprobado; ninguna fase se considera terminada ni validada por este documento.  
> **Herramienta de trabajo:** Claude Code, supervisado por el equipo.  
> **Directorio principal:** `~/Desktop/MAPA SOCIALTECH/` (o el directorio de escritorio devuelto por `xdg-user-dir DESKTOP`).

## 1. Objetivo

Partir de un **plano 2D** y producir un **escenario 3D funcional para Gazebo Harmonic**, acompañado del mapa y de la configuración necesarios para visualizar información del escenario en **RViz2 / ROS 2 Jazzy**. Se busca **minimizar el desarrollo propio**: primero investigar, instalar y probar software *open source* existente; permitir ajustes manuales o asistidos por IA cuando hagan falta. Se pretende respetar la **estructura y el modo de organización** de los simuladores de SocialTech anteriores, actualizando lo que no sea compatible con el entorno actual.

La progresión acordada es: **ejemplo sencillo de vivienda sin muebles → mapa de RViz2 → ejemplo con sillas, mesas y obstáculos → integración del Tracer → plano real de IQS → escenario de competición → entrega**.

No se utilizarán cámaras, Orbbec, grabaciones ni SLAM para reconstruir el espacio.

## 2. Información confirmada y pendiente

| Elemento | Estado |
| --- | --- |
| Sistema de trabajo del responsable | **Ubuntu 24.04 instalado de forma nativa**, no VirtualBox. |
| Pila objetivo | **ROS 2 Jazzy + Gazebo Harmonic + RViz2**. Confirmar instalación y funcionamiento al arrancar. |
| Robot | **Tracer**. Modelo/variante exacta, plugins y sensores **pendientes de verificar**. |
| Plano definitivo de IQS | **Aún no entregado**. |
| Formato y dimensiones reales del plano | **Desconocidos**. No inventar escala ni cotas. |
| Software de conversión | **Sin seleccionar ni validar**; compararlo y probarlo en F1/F2. |
| Requisitos de elementos específicos de competición | **Pendientes de confirmación**. |
| Trabajo en equipo | Archivos actuales del AGV en GitHub de Narcís; **no es necesario modificarlos** para la conversión inicial del plano. |

> El compañero que colabora en el mapa puede usar VirtualBox, pero **este proyecto se ejecutará y validará también en el Ubuntu nativo** del responsable. No confundir ambos entornos.

## 3. Repositorios que hay que estudiar antes de diseñar la solución

1. **SocialTech-Gazebo:** https://github.com/SocialTech-Challenge/SocialTech-Gazebo  
   Referencia principal para escenarios, modelos, mallas, definiciones de mundos, arranque y visualización. Comprobar directamente las carpetas `worlds/`, `models/`, `meshes/`, `launch/`, `urdf/`, `rviz/` y los archivos relevantes, incluyendo `ICAI_A501.world` y `models/aula_501/model.sdf` si están presentes en la revisión descargada.
2. **SocialTech-NOVNC:** https://github.com/SocialTech-Challenge/SocialTech-NOVNC  
   Referencia para comprender cómo se preparaba y ejecutaba el entorno anterior (Docker/noVNC y simulación). Identificar qué pertenece al entorno y qué pertenece realmente a la geometría del escenario.
3. **Repositorio actual del AGV (contexto para F5):** https://github.com/Narcis-Abella/socialtech-agv  
   No es prerrequisito para F0–F4. No modificarlo sin autorización.

**Regla:** documentar hechos confirmados con **ruta de archivo y revisión/commit**. No asumir que los componentes de **ROS 1 / Gazebo Classic** funcionan directamente con **ROS 2 Jazzy / Gazebo Harmonic**. Determinar qué formatos pueden conservarse y qué requiere adaptación.

## 4. Fases aprobadas y carpeta de cada una

| Fase | Carpeta | Trabajo | Resultado esperado |
| --- | --- | --- | --- |
| **F0** | `F0_AUDITORIA_REPOSITORIOS/` | Auditoría profunda de SocialTech-Gazebo y NOVNC. | Identificar formatos, estructura y funcionamiento. |
| **F1** | `F1_INVESTIGACION_SOFTWARE/` | Investigar y comparar herramientas *open source*. | Seleccionar, **con pruebas**, la solución más adecuada. |
| **F2** | `F2_PLANO_SIMPLE_GAZEBO/` | Convertir un plano sencillo de vivienda. | Vivienda 3D en Gazebo, sin muebles. |
| **F3** | `F3_MAPA_RVIZ2/` | Generar el mapa correspondiente para ROS 2 / RViz2. | Geometrías y coordenadas coherentes. |
| **F4** | `F4_ESCENARIO_CON_MOBILIARIO/` | Crear un segundo ejemplo con mesas, sillas y obstáculos. | Escenario 3D amueblado y funcional. |
| **F5** | `F5_INTEGRACION_TRACER/` | Integrar un Tracer simulado. | Robot representado dentro del escenario. |
| **F6** | `F6_PLANO_REAL_IQS/` | Recibir y procesar el plano oficial de IQS. | Espacio real reconstruido en 3D. |
| **F7** | `F7_ESCENARIO_COMPETICION/` | Añadir los elementos específicos de competición. | Escenario definitivo. |
| **F8** | `F8_VALIDACION_ENTREGA/` | Validación, documentación y entrega. | Simulador reproducible y verificado. |

### F0 — Auditoría de los repositorios originales

- Clonar los dos repositorios públicos **como referencias**, sin modificar su contenido. Registrar URL, rama y hash de commit.
- Inventariar los formatos **realmente utilizados**: `.world`, `.sdf`, `model.config`, mallas `.obj`/otros, configuración `.rviz`, launch, URDF y recursos referenciados; anotar qué archivos existen y cuáles no.
- Reconstruir las relaciones **mundo → modelo → malla → posición/rotación → colisión**, usando de ejemplo el aula anterior y sus objetos.
- Determinar cómo se inicia Gazebo y qué visualiza RViz en el sistema antiguo; diferenciar mapa 2D, configuración RViz y modelo 3D.
- Identificar incompatibilidades con Jazzy/Harmonic y definir la **estructura mínima equivalente** que tendremos que entregar.
- **Entregable:** `F0_AUDITORIA_REPOSITORIOS/informe.md`, con rutas, citas al código y dudas pendientes. **Cierre:** poder explicar cómo se componía y ejecutaba el escenario original, sin conjeturas.

### F1 — Investigación PRIORITARIA de software ya existente

- Buscar y revisar proyectos open source **mantenidos y documentados** capaces de transformar **planos 2D o mapas de ocupación** en geometría 3D/SDF para Gazebo; comprobar si generan también el mapa ROS 2, o si hace falta otra herramienta.
- **Candidatos a investigar, no seleccionados:** `map2sdf`, `image_to_gazebo` (ecosistema linorobot2), `scenery_builder` y otras alternativas que se encuentren. `sdf2map` puede evaluarse para la conversión de geometría SDF a mapas 2D si es compatible. No dar ninguna herramienta por válida sin verificar repositorio, instalación y prueba.
- Comparar **licencia**, estado de mantenimiento, documentación, entradas admitidas (imagen/PGM/PNG/PDF/DXF/DWG), necesidad de calibrar escala, salidas, colisiones, compatibilidad con **Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic**, capacidad de añadir muebles, limitaciones y trabajo manual necesario.
- Crear una **matriz comparativa con evidencias**, comandos reproducibles de instalación y un pequeño ejemplo para los candidatos más prometedores. Registrar fallos de compilación o renderizado.
- Priorizar la solución que requiera **menos programación propia**, sea fiable en geometría/escala y permita replicar la organización de SocialTech. Mantener una alternativa de reserva.
- **Entregable:** `F1_INVESTIGACION_SOFTWARE/comparativa.md` y evidencia de pruebas. **Cierre:** selección razonada basada en resultados reales, no en promesas del README.

### F2 — Primera prueba: vivienda simple, SIN mobiliario

- Elegir un plano de ejemplo **con dimensiones conocidas** y documentar su procedencia y escala.
- Preparar las entradas que requiera el software seleccionado; separar lo automático de las correcciones manuales.
- Convertir paredes, divisiones, suelo y accesos que permita identificar el plano; generar un mundo/modelos Gazebo válidos.
- Comprobar visualmente el mundo en **Gazebo Harmonic** y validar **escala, posición y colisiones**.
- **Entregable:** plano fuente, archivos de Gazebo y prueba de ejecución en `F2_PLANO_SIMPLE_GAZEBO/`.

### F3 — Mapa coherente y visualización en RViz2

- Obtener o generar el **mapa de ocupación** (por ejemplo, imagen + `.yaml`) a partir de la **misma geometría** del ejemplo F2.
- Establecer y documentar **resolución, origen, orientación, unidades y marcos**.
- Configurar ROS 2 para publicar el mapa y RViz2 para visualizarlo. **RViz2 no abre directamente un mundo `.world` como si fuera Gazebo.**
- Comparar puntos reconocibles del mundo 3D con el mapa 2D; corregir desajustes.
- **Entregable:** mapa, configuración RViz, pasos de arranque y evidencias de correspondencia en `F3_MAPA_RVIZ2/`.

### F4 — Segundo ejemplo: muebles y obstáculos

- Partir de un escenario de ejemplo y añadir **mesas, sillas y obstáculos** usando modelos reutilizables y permitiendo posición manual/IA asistida.
- Mantener la **separación entre aula base y modelos de objetos**, como en el enfoque de los repositorios originales.
- Verificar **mallas, materiales, posiciones, colisiones y rendimiento**; comprobar si el mapa 2D necesita reflejar muebles fijos u obstáculos para navegación.
- **Entregable:** mundo amueblado y evidencia de funcionamiento en `F4_ESCENARIO_CON_MOBILIARIO/`.

### F5 — Robot Tracer

- Identificar con evidencia la **variante concreta de Tracer**, su modelo simulado, controladores y sensores requeridos. Consultar lo necesario con José Ángel antes de decidir.
- Incorporarlo al mundo de ejemplo y verificar **posición, orientación, TF y visualización**; añadir movimiento/sensores solamente según requisitos confirmados.
- **Entregable:** lanzamiento reproducible del Tracer en el escenario de ejemplo en `F5_INTEGRACION_TRACER/`.

### F6 — Plano oficial de IQS

- Cuando llegue, registrar **formato, unidades, escala y dimensiones**; no dar nada por conocido antes de recibirlo.
- Aplicar la ruta de conversión validada en F1–F4. Si el formato exige pasos nuevos, investigarlos y probarlos antes de usarlos.
- Verificar geometría y colisiones con el plano recibido; dejar por escrito cualquier dato no disponible.
- **Entregable:** primera versión del escenario real IQS en `F6_PLANO_REAL_IQS/`.

### F7 — Escenario de competición

- Incorporar solo los **elementos de competición confirmados**: mobiliario, máquinas, obstáculos, checkpoints u otros si corresponde.
- Mantener modelo del aula, objetos independientes, posiciones y colisiones ordenados y verificables.
- **Entregable:** escenario de competición y mapa correspondientes en `F7_ESCENARIO_COMPETICION/`.

### F8 — Validación y entrega

- Confirmar que otro miembro del equipo puede **reproducir la instalación, generación y ejecución**.
- Verificar Gazebo, colisiones, mapa ROS/RViz2, escala, rendimiento, dependencias, licencia y archivos necesarios.
- Entregar instrucciones, comandos, resultados, capturas/logs y lista de limitaciones conocidas.
- **Entregable:** paquete final y documentación verificable en `F8_VALIDACION_ENTREGA/`.

## 5. Reglas para Claude Code

1. **Antes de cambiar código, investigar.** En particular F0 y F1 son prioritarias; no desarrollar un conversor propio por defecto.
2. **No inventar** medidas, formatos, modelos de robot, compatibilidad, funcionalidades de software ni resultados de pruebas.
3. Distinguir explícitamente **confirmado / por comprobar / fallido / no aplicable**; registrar comandos, versiones, archivos y evidencias.
4. Trabajar **dentro de `MAPA SOCIALTECH/`**; mantener los repositorios de referencia intactos y documentar cualquier copia/adaptación.
5. Colocar los informes, pruebas y entregables de cada fase **en su carpeta**; no crear carpetas paralelas sin necesidad.
6. No avanzar de fase solo por haber escrito archivos: comprobar el comportamiento real y obtener autorización del usuario para cerrar fases.
7. Si hay dudas sobre **SocialTech, requisitos de competición, plano o robot**, consultar con **José Ángel**.
8. Priorizar un resultado **simple, fiel y funcional** antes de añadir detalle visual.
9. Todo código nuevo debe tener un propósito necesario y documentado, idealmente un script de adaptación pequeño y reproducible.
10. Al acabar cada sesión, resumir **qué se hizo, qué se verificó, qué está pendiente y qué sigue**.

## 6. Cómo empezar en Claude Code

Abrir una terminal en el directorio `MAPA SOCIALTECH`, iniciar Claude Code allí y pedirle que **lea primero este documento completo**. Comenzar por **F0**, sin instalar conversores ni declarar ninguna alternativa ganadora hasta haber realizado la auditoría. Después continuar por **F1** con una comparación reproducible de herramientas open source.

**Primera orden sugerida a Claude Code:**

> Lee `PLAN_MAPA_SOCIALTECH.md`. Este es el plan aprobado del proyecto. No cambies las fases ni supongas detalles no confirmados. Comienza únicamente por **F0**: investiga a fondo los repositorios públicos SocialTech-Gazebo y SocialTech-NOVNC, registra las revisiones, identifica archivos y formatos reales, documenta cómo se compone y ejecuta el mundo anterior y detecta incompatibilidades con ROS 2 Jazzy/Gazebo Harmonic. Guarda el informe y evidencias en `F0_AUDITORIA_REPOSITORIOS/`. No modifiques repositorios de referencia. Al terminar informa de resultados, evidencias y cuestiones pendientes para aprobación antes de F1.
