# Prompt de relevo para continuar en la fase 5.2

Pega el bloque siguiente como primer mensaje en Claude Code, dentro de la carpeta del repo clonado.

````text
Eres mi asistente en el proyecto MAPA SOCIALTECH (SOCIALTECH IQS). Responde siempre en español.

REPO: https://github.com/JoseAngelCastaneda04/MAPA-SOCIALTECH (clonado en la carpeta actual).
Entorno objetivo: Ubuntu 24.04, ROS 2 Jazzy, Gazebo Harmonic (gz-sim 8.15), RViz2.

## 0. CONTEXTO
Objetivo: plano arquitectónico -> Gazebo Harmonic 3D -> mapa de ocupación en RViz2 -> mobiliario y máquinas -> simulación del AGV AgileX TRACER original.
Las fases F0 a F5 están CERRADAS y VALIDADAS EN SIMULACIÓN, CON LIMITACIONES DOCUMENTADAS. Esa validación NO implica equivalencia con el TRACER físico.

Antes de hacer nada, lee en este orden:
1. README.md y PLAN_MAPA_SOCIALTECH.md (definiciones de F6, F7 y F8).
2. F5_INTEGRACION_TRACER/RESUMEN F5.md y F5_INTEGRACION_TRACER/evidencias/DETALLE F5.md.
3. F5_INTEGRACION_TRACER/evidencias/ARCHIVOS PARA F6.md (guía clave: herramientas, procedimiento de 10 pasos, formatos, requisitos del plano, mobiliario y máquinas, limitaciones).
4. Los RESUMEN F1 a F4 y REPOS_EXTERNOS.md.

## 1. MISIÓN: FASE 5.2 (primera prueba real)
Hacer TODO lo que falta del proyecto, pero con el plano de la CASA DE JOSÉ en lugar del de IQS. Es el ensayo general: lo que no funcione aquí no funcionará con IQS, y lo que funcione se repite igual con IQS.
Trabaja como si fuera la entrega definitiva:
a) Equivalente a F6: importar y convertir el plano de la casa (DXF/DWG preferido; PDF solo si es vectorial; imagen solo con una cota real de escala), generar mundo de Gazebo y mapa de ocupación. Mide el error en metros con al menos 6 cotas de control reales.
b) Equivalente a F4: mobiliario y "máquinas" como modelos independientes, desde medidas reales o fichas, incluyendo objetos en medio de las salas. Cuida la altura: el LiDAR del TRACER está a ~0,20 m y no ve mesas ni tableros por encima.
c) Equivalente a F5: integrar el TRACER en el nuevo mapa (TF, LiDAR, watchdog, RViz2) y comprobar que se navega con teleop.
d) Equivalente a F7: elementos de competición (checkpoints, zonas, rutas, lo que defina PLAN_MAPA_SOCIALTECH.md), con datos de ejemplo marcados como tales.
e) Equivalente a F8: validación y entrega: pruebas reproducibles, mediciones, capturas, documentación final y limitaciones.
f) Entrega en GitHub y reinstalación: otra persona debe poder clonar el repo y dejarlo todo funcionando solo con las instrucciones.
   - Valida desde cero RESTAURAR_ENTORNO.sh (NO ha sido probado en una copia limpia) y corrígelo si falla.
   - Escribe INSTALACIÓN y USO paso a paso: requisitos, instalación, demo, regenerar el mapa desde un plano nuevo, problemas conocidos.
   - Repo ordenado, sin binarios enormes (GitHub rechaza archivos de más de 100 MB) y con README actualizado.
   - Documenta el procedimiento genérico "cómo se haría con el plano de IQS", paso a paso.

## 2. ORGANIZACIÓN
- NO modifiques F0 a F4 (solo lectura) ni sobrescribas nada de F5.
- Crea carpetas nuevas (por ejemplo F5_2_CASA_JOSE/ con subcarpetas por apartado) y copia dentro lo que necesites de F2 a F5.
- Los scripts de F4 tienen rutas fijas a F2/F3: cámbialas al copiarlos.
- Cada apartado lleva "RESUMEN <fase>.md" (~2 páginas) y un anexo "evidencias/DETALLE <fase>.md".
- Reutiliza las herramientas de F1: LibreDWG (DWG->DXF), ezdxf, dxf_a_mapa.py, raster_a_mapa.py, map2sdf (0,02 o 0,01 m/celda), sdf2map + combinar_mapas.py y el pipeline YAML de mobiliario de F4.
- Guarda pruebas y mediciones como evidencia y no borres evidencia.

## 3. REGLAS (obligatorias)
- NO inventes dimensiones del espacio real. Si falta una cota, el plano o la altura de un objeto, pregúntame. No construyas sin el plano.
- NO conectes el TRACER físico ni toques la Jetson. Todo es simulación.
- El watchdog (F5_INTEGRACION_TRACER/scripts/watchdog_cmd_vel.py) es SOLO de simulación: NO es parada de seguridad ni fail-safe.
- No presentes como validadas velocidades de 1,5 m/s: la zona validada es 0,2 m/s y 0,5 rad/s.
- No instales herramientas adicionales sin preguntarme (di qué es y por qué).
- Cierra procesos solo por PIDs o grupos de proceso guardados, nunca por patrón de nombre. Antes de lanzar pruebas comprueba que no hay otro Gazebo en marcha.
- Capturas solo con pantalla aislada (Xephyr, scripts/captura_aislada.sh), nunca del escritorio.
- Informa con honestidad: si algo falla o no se probó, dilo. No declares una fase cerrada sin mi autorización expresa.
- Antes de hacer push a GitHub, pregúntame. El plano de una casa es un dato personal: confirma que el repo es privado antes de subirlo.
- Licencias: las mallas de tracer_ros no tienen licencia y no se redistribuyen (se enlazan con RESTAURAR_ENTORNO.sh). Comprueba la licencia de cualquier plano o modelo antes de subirlo.

## 4. PRIMEROS PASOS
1. Lee los documentos del apartado 0 y resume en 10 líneas lo que has entendido.
2. Ejecuta RESTAURAR_ENTORNO.sh en limpio y comprueba F5_INTEGRACION_TRACER/scripts/demo.sh con teleop.sh y parar_demo.sh. Informa del resultado.
3. Dime qué necesitas de mí o de José para la casa: plano DXF/DWG/PDF vectorial; unidades, origen y 6+ cotas de control; alturas y puertas; lista de muebles y "máquinas" con medidas.
4. Con los datos, propón un plan por apartados (a a f) y espera mi OK antes de ejecutarlo.
````
