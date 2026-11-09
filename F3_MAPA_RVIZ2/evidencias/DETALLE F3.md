# DETALLE F3 — comandos, resultados y límites (anexo de `RESUMEN F3.md`)
Rutas relativas a `F3_MAPA_RVIZ2/`; `F2/` = `../F2_PLANO_SIMPLE_GAZEBO` (solo lectura). ROS 2 Jazzy, Gazebo Sim 8 (Harmonic), RViz2, Ubuntu 24.04, Mesa/Intel (RViz2 y Gazebo; NVIDIA presente pero no usada por RViz2: sus mapas de memoria solo cargan Mesa).

## A. Archivos usados
| Qué | Ruta |
|---|---|
| Mapa 1 cm (copia) | `mapa/piso_1cm.{pgm,yaml}`; SHA del PGM idéntico al de `F2/mapa/` (`e0b52cb2…`). 1350×1179, 0,01, origen [4,7299; −11,32; 0], `trinary`, `negate 0`, 0,65 / 0,196 |
| Mapa 2 cm (copia) | `mapa/piso_2cm.{pgm,yaml}` (de `F2/mapa/piso.*`, solo cambia el nombre de imagen) |
| Mundo / modelo | `F2/mundo/piso_designscad_1cm.sdf`, `F2/mundo/modelos/piso_designscad_1cm/` (`model.sdf` pose [4,7299; −11,32; 0], STL 1 540 triángulos) |
| Verdad geométrica | `F2/derivados/plano_piso_muros.dxf` (m; capas `ESTRUTURA - ARQ-STA - BLOCOS_ESTRUTURAIS` y `F2_LAZOS_ALVENARIA`, como en F2), `F2/evidencias/cotas_verificadas.json` |

## B. Servidor de mapas y estados
`scripts/prueba1.sh`: `nav2_map_server map_server -p yaml_filename:=…` + `nav2_lifecycle_manager -p autostart:=true -p node_names:="['map_server']"`. Resultado: `ros2 lifecycle get /map_server` → `active [3]`; `/map` con 1 publicador, QoS RELIABLE + TRANSIENT_LOCAL (necesario en RViz2: Durability *Transient Local* en `config/piso_1cm.rviz`). Transiciones manuales comprobadas: configure, activate, deactivate, cleanup (en `logs/rendimiento_*.txt`). Cabecera recibida: 1350×1179, res 0,01, origen (4,7299; −11,32), orientación identidad, `frame_id map`.
El `launch/mapa_rviz.launch.py` hace lo mismo y añade `static_transform_publisher --frame-id map --child-frame-id world` (identidad) y RViz2.

## C. Avisos (paso 1 de tu instrucción)
1. **Global Status**: panel expandido (`capturas_rviz/02_global_status.png`): `Fixed Frame: No tf data. Actual err…`. Prueba: lanzar solo el TF estático → `03_status_con_tf_estatico.png` «Global Status: Ok». Control: el GLSL sigue en el log tras ese cambio → **no relacionados**.
2. **GLSL**: `[ERROR] rviz/glsl120/indexed_8bit_image.vert … active samplers with a different type refer to the same texture image unit` (aparece 1 vez por arranque, al crear el display Map). Renderer: Mesa (libgallium 25.2.8, Intel TigerLake GT1). Efectos medidos: píxeles libres (255,255,255) y ocupados (0,0,0); tamaño del mapa en pantalla 13,5 × 11,8 m (esperado 13,5 × 11,79); caja de muros 13,086 × 11,386 m (CAD 13,09 × 11,39; 1 px = 0,0143 m a 70 px/m). Rendimiento: 5 % CPU, 31 fps. No se tocó ningún driver ni configuración global. 🔎 No sé qué técnica de reserva usa Ogre ni si afectaría a otros esquemas de color.

## D. Comparación (comandos y salida)
```bash
source /opt/ros/jazzy/setup.bash
python3 scripts/volcar_mapa_topic.py evidencias/logs/map_topic_1cm.npz      # guarda lo recibido por /map (como RViz2)
../F1_INVESTIGACION_SOFTWARE/herramientas/venv/bin/python -I scripts/comparar_geometria.py evidencias/logs/map_topic_1cm_arranque2.npz evidencias/logs/comparacion_geometria.json
```
Método: (1) `/map` (datos del tópico, volteados porque `OccupancyGrid` empieza por y mínima); (2) STL + pose del `model.sdf`; (3) polígonos del DXF con `poligonos()` de F1 importado sin escribir bytecode. Rejilla común 2,5 mm con el criterio de F1 (supersampling ×4, ocupada si ≥ 49 %): así el área del CAD sale **10,534 m²**, igual que la «verdad» de F2. *(Mi primer rasterizado inflaba los bordes —10,75 m²— y lo corregí.)* Las puertas y cotas se miden **cortando a lo largo del eje**: CAD analítico con los polígonos; STL analítico con las caras verticales a z = 0,05 / 1,25 / 2,45 m y con la tapa; mapa por celdas. Salida completa: `logs/comparacion_geometria.{json,txt}`.

Resultados clave (m): `dimensiones` — tamaño CAD = STL = mapa ocupado = [13,09; 11,39]; STL altura 2,5; extensión del mapa [13,5; 11,79]; márgenes [0,20; 0,20; 0,21; 0,20]; escala STL/CAD 1,00000. Áreas 10,534 / 10,551 / 10,559. IoU mapa-CAD 0,99823; STL-CAD 0,99750; mapa-STL 0,99921. Desviación de borde mapa→CAD: media 0,0001, p99 0,005, máx. 0,0075; STL→CAD máx. 0,009. Habitaciones (erosión 0,46 m > semihueco 0,45 m): 7 en las tres; distancia entre centros mapa-CAD [0, 0,001, 0, 0, 0, 0, 0].

| Puerta/cota (eje) | Hueco CAD (m) | Mapa | STL (z 0,05/1,25/2,45 iguales) | Ancho |
|---|---|---|---|---|
| WC izq. (x) | 10,970 – 11,880 | igual | igual | 0,91 |
| WC der. (x) | 15,570 – 16,480 | igual | igual | 0,91 |
| Dorm. 1 (x) | 11,220 – 12,130 | −0,0001 | −0,0001 | 0,91 |
| Dorm. 2 (x) | 12,370 – 13,280 | igual | igual | 0,91 |
| Dorm. 3 (y) | −6,830 – −5,820 | igual | igual | 1,01 |
| Entrada (y) | −3,6624 – −2,1200 | −3,6600 (+0,0024) | −3,6628 (−0,0004) | 1,5424 / 1,54 / 1,5428 |
Los números del mapa y del CAD coinciden porque el CAD está en múltiplos de 1 cm y el origen se alineó con él (esquina − 0,2 m); no es una coincidencia sospechosa, pero conviene saberlo.

## E. Medición sobre píxeles de RViz2
`scripts/medir_rviz.py evidencias/capturas_rviz/medicion` (vista cenital ortogonal, sin rejilla ni ejes; una instancia de RViz2 por vista; solo se captura su ventana). Vista completa 70 px/m: mapa 945×826 px = 13,50 × 11,80 m; caja de muros 13,086 × 11,386 m; margen izq. 0,200 m, inf. 0,214 m (1 px = 0,014 m). Puertas a 300 px/m (1 px = 3,3 mm), anchura del tramo libre: 273 / 273 / 273 / 273 / 303 / 462 px = **0,91 / 0,91 / 0,91 / 0,91 / 1,01 / 1,54 m**, ninguna toca el borde de la vista. Capturas: `capturas_rviz/medicion/*.png`.

## F. Rendimiento (`scripts/rendimiento.sh <yaml> <s> <salida>`)
Datos crudos en `logs/rendimiento_1cm.txt` (180 s, 36 muestras) y `_2cm.txt` (60 s). RSS RViz2 195 476–195 884 kB (1 cm) estable; RSS servidor 48 384 kB constante; CPU servidor 0,18 %. Carga: «Loading yaml» → «Read map» = 22,3 ms (1 cm) y 7,1 ms (2 cm). Los ≈1 s de `configure`/`activate` medidos desde fuera son sobre todo el arranque de la CLI `ros2`. Tras 20 ciclos: RSS servidor 72 672 kB (1 cm), 50 868 kB (2 cm). Capturas: `logs/rendimiento_*_rviz.png`. La «fluidez» es la lectura de la barra de RViz2 (31 fps), no una medida independiente.

## G. Demostración
Scripts: `scripts/demo.sh`, `demo_gazebo.sh` (exporta `GZ_SIM_RESOURCE_PATH` y `SDF_PATH` a `F2/mundo/modelos`; cámara cenital `move_to/pose` (11; −5,4; 15), como F2), `parar_demo.sh`, `launch/mapa_rviz.launch.py`.
Arranque 1: sin procesos previos; tras 25 s: `map_server` active, `/world/piso_designscad_1cm/pose/info` → `piso` en (4,7299; −11,32), orientación identidad; Global Status Ok; capturas en `capturas_gazebo/` y `capturas_rviz/04`. `parar_demo.sh` → sin restos. Arranque 2: igual, `/map` idéntico al del arranque 1 (`cmp`), `pose/info` igual; captura de RViz2 `05`; la de Gazebo no se obtuvo (mi error de PID). Avisos de Gazebo: solo `libEGL warning … failed to create dri2 screen`, ya presentes en los logs de F2 (`gz_gui_1cm.log`). Logs: `logs/demo_*_arranque1.log`.
Incidencias propias: clase de vista `TopDownOrthographic` inexistente (es `TopDownOrtho`); mi script de captura elegía una ventana oculta (corregido); un `pkill -f` mató mi propia shell (sin efecto en datos).

## H. Cosas no hechas (aceptadas en el cierre)
RViz2 con la NVIDIA; prueba larga de memoria; ventanas, hoja corredera y baranda; ninguna modificación de F0–F2; sin mobiliario, checkpoints ni Tracer.

## I. Cierre (autorizado el 2026-11-08)
**F3 CERRADA Y VALIDADA para el escenario probado** (un piso, 0,01 m/celda, Mesa/Intel, color «map»). Decisiones: 0,01 m principal; GLSL y NVIDIA sin más investigación (**sin impacto funcional observado**); aumento de RAM del servidor tras 20 ciclos = **observación pendiente, no se afirma fuga** (1 cm: 48 384→72 672 kB; 2 cm: 42 720→50 868 kB, `logs/rendimiento_*.txt`); TF identidad `map→world` válido hoy, **a revisar en F5 con el Tracer**. Sin cambios en mediciones, capturas, logs, configuración ni scripts desde el último informe. Comprobado al cerrar: ningún proceso de la demo en ejecución. Reutilizable en F4: `evidencias/ARCHIVOS PARA F4.md`.
