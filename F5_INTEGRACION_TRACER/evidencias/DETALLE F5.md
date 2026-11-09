# DETALLE F5 — Anexo de `RESUMEN F5.md`
Rutas relativas a `F5_INTEGRACION_TRACER/`. Fecha de trabajo: 2026-11-09. Todo es simulación.

## 1. Fuentes consultadas y licencias
| Fuente | Contenido relevante | Licencia | Soporte Jazzy + Harmonic |
|---|---|---|---|
| `agilexrobotics/tracer_ros` (F0, `774ba0f`, 2021; rama `master` actualizada 2025-08) | `tracer_description` (URDF/xacro, mallas `.dae`/`.stl`), `tracer_gazebo_sim`, `tracer_base` | **Sin archivo LICENSE** (API de GitHub: sin licencia). `package.xml`: BSD en base/bringup/msgs/gazebo_sim; **`tracer_description`: `TODO`**. Los xacro de ruedas llevan cabecera BSD de Clearpath/Weston Robot | No: ROS 1, ros_control, Gazebo Classic |
| `agilexrobotics/tracer_ros2` (rama `humble`) | solo `tracer_base`, `tracer_msgs` | Apache-2.0 | No trae descripción ni simulación |
| `agilexrobotics/ugv_gazebo_sim/tracer` | `tracer_description`, `tracer_gazebo_sim` (Melodic) y `tracer2_description` (URDF de SolidWorks, STL) | **Sin LICENSE** | No: ROS 1 / Gazebo Classic |
| `agilexrobotics/ugv_sdk` (F0, `20d85ec`) | protocolo CAN | Apache-2.0 | Solo robot real; no usado |
Las páginas de GitHub devolvieron 504 desde WebFetch; el contenido se leyó con `gh api` (listados y archivos). No pude leer los README de `tracer_ros2`. **Consecuencia:** las mallas se usan **solo en local mediante enlaces simbólicos** a F0 (`modelos/tracer_agv/meshes/*.dae`); no se copian ni se redistribuyen. Si el proyecto se publica, hay que pedir permiso a AgileX.

## 2. Comparación de modelos (mallas medidas con `scripts/medir_malla.py`)
| | Tracer original (`tracer_ros`) | Tracer 2.0 (`ugv_gazebo_sim/tracer2_description`) | «tracer2» SocialTech 2025 (F0) |
|---|---|---|---|
| Chasis (X × Y × Z, m) | 0,685 × 0,570 × 0,130 | 0,704 × 0,610 × 0,143 | 0,685 × 0,570 × 0,145 (malla de 1 242 vértices) |
| Rueda motriz | Ø 0,121, anch. 0,0844; y = ±0,17 | Ø 0,125 (`right_link`/`left_Link`) | Ø 0,125, anch. 0,075; y = ±0,13 |
| Separación que usa su plugin | 0,34 (wheelbase del xacro) | — | **0,335** (plugin) frente a **0,26** (juntas del URDF): inconsistente |
| Ruedas locas | 4, malla Ø 0,0744 | 4, malla ~0,096 | 4 «apoyos» Ø 0,059 |
| Masa en su URDF | `inertial_link` 132,39 kg (sin justificar; 44,39 kg comentado) y 6 kg por rueda | — | 42,875 kg |
| LiDAR | — | — | `rslidar_link` en (0,2125; 0; 0,20), cilindro r 0,03 × 0,07; plugin «hokuyo» (180°, 720 haces, 0,1–30 m, 40 Hz) |
| Origen `base_link` | centro entre ruedas motrices, 0,082 m sobre su eje | — | a nivel del suelo (rueda r 0,0625 con centro a 0,0625) |
Lectura: el chasis de SocialTech coincide con el del **original** (685 × 570) y sus ruedas con las del **2.0** (Ø 0,125); por eso «tracer2» **no prueba** que sea el 2.0 comercial. No se tomaron datos de ese modelo para el robot (solo el dato del lidar como referencia, §7).

Especificaciones comerciales (búsqueda web; no oficiales de AgileX salvo que se indique): 30 kg, 100 kg de carga, 1,6 m/s sin carga, holgura 30 mm, motores 2 × 150 W, batería 24 V (Trossen Robotics, RobotLAB: 660 × 516 × 163,5 mm; Robosavvy: 685 × 570 × 155 mm, vía 360 mm). El Tracer 2.0 comercial (702 × 610 × 169 mm, ~54–56 kg, 2 m/s) **no se usó**. No pude acceder a la hoja de datos de AgileX: **la discrepancia de dimensiones entre vendedores queda sin resolver**; la malla (685 × 570 × 164,5) coincide con Robosavvy en planta y con Trossen en altura (163,5 mm).

## 3. Valores del modelo: confirmado / medido / estimado
| Parámetro | Valor | Origen |
|---|---|---|
| Chasis, ruedas, ruedas locas, posiciones | ver §2 | **medido** en mallas/URDF oficiales |
| Altura del chasis sobre el suelo | 0,0343 m | calculada (malla, −0,1082 + 0,1425); doc. 0,030 m |
| Velocidad máxima | 1,6 m/s | **documentado** (vendedores); `max_linear_velocity` del plugin |
| Velocidad angular máxima, aceleración | sin límite | **no documentado**; no se inventó |
| Masa total | 30 kg | **documentado** (peso en vacío) |
| Reparto: chasis 26 kg, ruedas 1 kg c/u, locas 0,5 kg c/u | | **estimado** |
| Inercia del chasis | caja homogénea 0,685 × 0,57 × 0,13 | **estimado** |
| Centro de gravedad | (0, 0, −0,043) m en `base_link` | **estimado** (centro de la caja de la malla); no documentado |
| Fricción: motrices μ = 1,0 (kp 1e6, kd 100), locas 0,02, chasis 0,3 | | **estimado** (las del xacro original eran μ1 = 1,0, μ2 = 0,9, kp 1e7) |
| Sistema de tracción | diferencial (2 motrices + 4 locas) | **documentado** (xacro: 2 juntas continuas motrices; 150 W × 2 por vendedor) |
| `base_link` | del fabricante; añadido `base_footprint` en el suelo (0,1425 m debajo) | decisión mía |

## 4. Adaptaciones a ROS 2 Jazzy / Gazebo Harmonic
- `urdf/tracer_agv.urdf.xacro` (única fuente) → `scripts/generar_robot.sh` genera `urdf/tracer_agv_rviz.urdf` (mallas `file://`, sin extensiones Gazebo) y `modelos/tracer_agv/model.sdf` (con `gz sdf -p`; `Valid.`).
- Plugins: `gz-sim-diff-drive-system` (`/cmd_vel`, `/odom`, `/tf`; `frame_id odom`, `child_frame_id base_footprint`; 50 Hz; `wheel_separation` 0,34; `wheel_radius` 0,0605), `gz-sim-joint-state-publisher-system` (ruedas motrices), `gpu_lidar` + `gz-sim-sensors-system` (ogre2) en el mundo. Nada de ros_control ni plugins Classic.
- **Conservado del fabricante:** mallas `.dae` (chasis sin ruedas, rueda, rueda loca, horquilla), posiciones de ruedas y pivotes, eje de las juntas motrices.
- **Cambios (todos mencionados en el xacro):** giro `Rx(π/2)` exacto en lugar de 1,57; colisión del chasis = **casco convexo simplificado** de la malla (`scripts/generar_colision.py`: 97 609 vértices → 277 vértices / 550 caras; el casco omite como mucho **5,2 mm** (p99 2,9 mm); volumen 0,0395 frente a 0,0403 m³ del casco exacto; un casco rellena concavidades: es conservador); ruedas motrices **esféricas** (§3 de RESUMEN, error 2); ruedas locas **fijas** con cilindro de colisión r 0,0372 × 0,053 y μ 0,02 (el fabricante: 2 juntas continuas por rueda); sin transmisiones ros_control; dos errores corregidos (RESUMEN §4). El OBJ de colisión lleva una normal por cara porque dartsim **aborta** sin normales (me pasó).
- Estructura: `base_footprint → base_link → {left_wheel_link, right_wheel_link (juntas continuas `left_wheel`, `right_wheel`, eje +Y), 4 `*_castor_link` (fijas), laser (fija)}`. Los dos ejes +Y: rotación positiva = avance.

## 5. Tópicos (verificados con `ros2 topic info`) — `config/bridge.yaml`
| ROS 2 | Tipo ROS | Gazebo | Dirección |
|---|---|---|---|
| `/cmd_vel` | `geometry_msgs/msg/Twist` | `gz.msgs.Twist` | ROS→GZ (no es `TwistStamped`) |
| `/odom` | `nav_msgs/msg/Odometry` | `gz.msgs.Odometry` | GZ→ROS, 50,0 Hz |
| `/tf` | `tf2_msgs/msg/TFMessage` | `gz.msgs.Pose_V` | GZ→ROS (solo `odom→base_footprint`) |
| `/joint_states` | `sensor_msgs/msg/JointState` | `gz.msgs.Model` | GZ→ROS, **1 000 Hz** |
| `/scan` | `sensor_msgs/msg/LaserScan` | `gz.msgs.LaserScan` | GZ→ROS, 10,0 Hz, `frame_id: laser` |
| `/clock` | `rosgraph_msgs/msg/Clock` | `gz.msgs.Clock` | GZ→ROS, 1 000 Hz |
`/gz/odom_gt` (verdad de terreno, solo mundo `_gt` y `scripts/puente_verdad.sh`): `OdometryPublisher` dentro del `<include>` del mundo, no del robot. Frecuencias medidas con `scripts/medir_frecuencias.py` (`ros2 topic hz` no devolvió datos en este entorno).

## 6. TF (`scripts/comprobar_tf.py`, `logs/tf_auditoria.json`)
Publicadores: `map→odom` `static_transform_publisher` (pose de `config/inicio.yaml`); `odom→base_footprint` DiffDrive (50,1 Hz); `base_footprint→base_link`, `base_link→laser/castores` (`/tf_static`) y ruedas (dinámicas) `robot_state_publisher`. Prueba: avanzar 0,1 m/s 10 s y girar 0,5 rad/s 12 s, arrancando el sistema justo antes. **Una auditoría anterior dio 0,31 m / 27° de error: era mía** (se solapaban dos sistemas, uno con el robot ya bloqueado contra mobiliario; se repitió con un solo Gazebo y `ya hay una simulación activa` ahora se detecta en `lanzar_pruebas.sh`). El criterio de extrapolación usa marcas de 20 ms con 60 ms de margen. Resultado en RESUMEN §3.

## 7. LiDAR
- Configuración de prueba: `gpu_lidar` en `laser`, a (0,2125; 0; 0,20) m sobre el suelo (altura y posición **copiadas del modelo 2025, no verificadas**), 360°, 720 haces (el barrido incluye ±π, 719 pasos), rango 0,10–30 m, 10 Hz, sin ruido. El 2025 declaraba 180°, 40 Hz y ruido gaussiano σ = 0,01 m (plugin «hokuyo» sobre un enlace «rslidar»): **no se sabe qué sensor es el físico**.
- Rango real: ver `logs/lidar_vs_mapa.json` (5 poses; error mediano frente al trazado de rayos sobre el mapa 2,3–4,7 mm, p95 hasta 2,97 m cuando hay objetos que el lidar no ve).
- **Qué ve y qué no (poses del salón):** el LiDAR **ve** paredes y la caja (haces dentro de 3 cm del mapa: 74 %, 74 %, 90 %, 99,5 % y 94 % según la pose). **No ve** las sillas: de 720 haces, 66 y 50 (`salon_libre`: silla_N, silla_E), 82/39/39 (`frente_mesa_sillas`) y 31/19 (`junto_caja`) atraviesan una silla que el mapa dibuja; ni tableros (mesa a 0,74–0,80 m) ni asientos (0,35–0,43 m). Solo ve patas/poste. En `entre_mesa_papelera` y `ante_puerta` el acuerdo es 99,5 % y 93,8 %.
- Colisiones frente a lo visible: las **sillas bloquean al robot** (base de F4 estimada) pero el LiDAR a 0,20 m **no las detecta bien**; las mesas bloquean por la malla de colisión y el LiDAR solo ve sus patas. Para navegación futura hay que decidir si la banda del mapa (0,05–1,8 m, no cambiada) debe seguir incluyendo tableros y asientos (**conservador, coherente con el robot**) o limitarse a lo visible a 0,20 m. No se cambió ni se midió otra banda: queda para ti/F6+.

## 8. Pruebas de movimiento (`logs/mov_vacio.json`, `logs/mov_vacio.txt`)
Verdad de terreno = `/gz/odom_gt` a 100 Hz; duración real medida en tiempo de simulación (la orden se publica a 20 Hz). Todas las cifras (Gazebo − esperado; odom − Gazebo; deriva tras parar):
| Prueba | Gazebo − esperado | Odom − Gazebo | Deriva tras `v=0` |
|---|---|---|---|
| A 0,1 m/s × 4 s | −1,6 mm | −0,5 mm | 1,6 mm |
| A 0,3 | −8,4 mm | +1,8 mm | 7,8 mm |
| A 0,6 | −25,8 mm | +13,2 mm | 26,9 mm |
| A 1,0 × 2 s | −64,7 mm | +42,7 mm | 65,4 mm |
| A 1,5 × 2 s | −135,3 mm | +103,8 mm | 138,7 mm |
| A −0,3 (atrás) | +10,5 mm | −4,2 mm | 8,0 mm |
| B ω 0,2 / 0,5 / 1,0 / 1,5 (90°) | −0,10° / −0,50° / −1,61° / −3,07° | −0,08° / −0,02° / +1,09° / +1,60° | 0 mm |
| B −0,5 (derecha) | +0,52° | +0,02° | 0 |
| C 0,3 / 1,0 m/s × 3 s y giro ω 1,0 × 2 s | −7,4 / −61,7 mm; yaw −1,66° | +1,7 / +42,7 mm; +0,52° | 7,2 / 63,4 mm / 0 |
| D v 0,3 ω 0,3 | 4,4 mm avance; −13,2 mm lateral; −0,75° | −4,8 mm; +0,43° | 7,3 mm |
| D v 0,5 ω −0,4 | +28,2 / +30,4 mm; +1,51° | −24,3 mm; −1,08° | 16,4 mm |
| D v 0,8 ω 0,8 | +94,0 / +59,5 mm; −4,65° | −84,0 mm; +3,78° | 35,4 mm |
| D v −0,3 ω 0,3 | −5,5 / +17,2 mm; −0,98° | +5,9 mm; +0,64° | 7,6 mm |
| E cuadrado ×3 | 0,089–0,090 mm de cierre; 0,0002° | | |
Interpretación (no un margen impuesto): el déficit crece con la velocidad ~ `v · 0,09 s`: es la **respuesta de la rueda** (el controlador no es instantáneo); odometría y Gazebo discrepan en aceleraciones bruscas por patinaje. La repetibilidad absoluta (0,09 mm) es la de un simulador determinista: **no estima la del robot real**. Los comandos eran escalones sin límite de aceleración; el robot real lo tendrá.

## 9. Colisiones (`logs/colisiones.json`)
A 0,3 m/s desde `set_pose`; la parada prevista es el barrido de la **huella** (polígono real orientado) por el mapa de F4 (`scripts/barrido_mapa.py`); contacto = primera celda ocupada.
| Prueba | Inicio (x, y, yaw°) | Parada real | Prevista (mapa) | Diferencia | z máx / cabeceo máx |
|---|---|---|---|---|---|
| Pared norte | 9,70; −2,70; 90 | 0,4375 | 0,44 | −2,5 mm | 0,02 mm / 0,06° |
| mesa_1 | 8,20; −2,70; −90 | 1,5134 | 1,52 | −6,6 mm | 1,7 mm / 0,08° |
| silla_N (de frente) | 8,90; −2,70; −90 | 0,8784 | 0,84 | **+38,4 mm** | 1,8 mm / 0,13° |
| silla_E (costado) | 10,05; −2,70; −90 | 1,6284 | 1,63 | −1,6 mm | 1,5 mm / 0,13° |
| caja_1 | 12,50; −6,30; 180 | 1,7575 | 1,75 | +7,5 mm | 2,0 mm / 0,13° |
| Puerta dorm.3 (1,01 m) | 12,20; −6,325; 0 | 3,5998 (pasa 3,6 m libres) | libre | — | 1,5 mm / 0,16° |
| Puerta dorm.1 (0,91 m) | 11,675; −8,00; 90 | 1,860 | 1,87 (muro tras la puerta) | −10 mm; deriva lateral −17 mm, giro −0,77° | 2,0 mm / 0,06° |
- **Qué prueba:** que la geometría de colisión del robot y la del mobiliario bloquean donde el mapa dice, a ≤ 1 cm (el mapa tiene 1 cm/celda). **No prueba** nada sobre la silla real (§8 RESUMEN).
- **silla_N +38 mm:** el robot avanza 3,8 cm más de lo que bloquea el mapa porque el respaldo (z ≥ 0,43 m) está sobre el robot (altura 0,1645 + lidar 0,235 m) y solo frena la base de F4 (cilindro 0,25 × 0,04 m): el mapa es **conservador**.
- En todos los casos la odometría siguió acumulando (`odom_recorrido_m` mayor que el real): 1,05 frente a 0,44 m en la pared.
- No probé el papelero (el mapa lo deja a 0,18 m de un muro: no hay carril libre para la huella de 0,57 m); `silla_S`/`silla_W` no se probaron por separado.

## 10. RViz2 frente a Gazebo
- Numérico: `map→base_footprint` (la cadena que dibuja RViz2) frente a Gazebo: 0,9 mm / 0,37° (RESUMEN §3).
- Pixeles (`scripts/medir_rviz_pixeles.py`, `logs/rviz_pixeles.json`; display aislado Xephyr, 110 px/m = 9,1 mm/px; calibración: muros del PGM frente a negros dibujados, IoU 0,91): 250 puntos del LiDAR detectados; distancia al obstáculo del mapa: mediana 0,000 m, p90 0,010 m, **máx. 0,020 m**, 100 % ≤ 2 cm. Esto valida la cadena pose + montaje del lidar; **no** mide por separado la pose del modelo 3D del robot (la malla se dibuja con la misma TF). 🔎 La coincidencia con el render de Gazebo sigue siendo cualitativa (capturas).

## 11. Rendimiento (`logs/rendimiento_*.json`, `scripts/medir_servidor.sh`, `medir_rendimiento.py`)
| Servidor Gazebo headless, 15 s | Carga hasta `/clock` | RAM | CPU |
|---|---|---|---|
| F4 (sin robot) | 4,54 s | 183 MB | 26 % |
| F5 sensores, sin robot | 4,53 s | 185 MB | 29 % |
| F5 + TRACER sin LiDAR | 4,51 s | 197 MB | 54 % |
| F5 + TRACER + LiDAR | 4,51 s | **496 MB** | 58 % |
Causas: el robot dinámico (6 contactos a 1 kHz) cuesta ~+28 puntos de CPU; el LiDAR no sube la CPU pero **arranca ogre2: +300 MB**. RTF = 0,999 en todos los casos. Sistema completo con GUI real y RViz2 (20 s en reposo y 20 s girando): servidor 487 MB / 93 %, GUI 627 MB / 130 %, RViz2 331 MB / 43–49 %, puente 58 MB / 31 %, `robot_state_publisher` 36 MB / 16 %, resto de nodos ROS 8–9 % cada uno. **Comparación con F4:** F4 midió GUI 524 MB/137 % y RViz2 192 MB/3 % (con otros nodos). No separé cuánto de RViz2 se debe a `RobotModel` (97 k triángulos) y cuánto al reloj/`/joint_states` a 1 kHz; los nodos con `use_sim_time` (estático, lifecycle) gastan 7–9 % solo por recibir `/clock` a 1 kHz. **Optimizaciones sencillas pendientes (no aplicadas, afectarían a la precisión):** pasar el paso de física de 1 ms a 2 ms, o filtrar `/clock` y `/joint_states` en el puente.
Errores/avisos: 0 errores de Gazebo; `gz_frame_id` (aviso de sdformat, funciona); `libEGL warning` (driver, ya en F4); RViz2: el GLSL de F3.

## 12. Demostración y cierre
`scripts/demo.sh` regenera el mundo (pose de `config/inicio.yaml`), lanza Gazebo (GUI, cámara cenital), el puente, `robot_state_publisher`, `map_server` (mapa de F4, solo lectura) y RViz2 (`rviz/tracer_piso.rviz`). `scripts/parar_demo.sh` cierra por grupos de procesos guardados en `/tmp/f5_demo/*.pid` (sin `pkill` por nombre). **3 arranques desde cero:** `/map` 1 350 celdas de ancho, `/scan` con frame `laser`, 7 nodos; **0 procesos residuales** tras cada cierre. `demo.sh` se niega a arrancar si ya hay una demo viva. Teleoperación: `scripts/teleop.sh` (0,2 m/s, 0,5 rad/s; parada automática a los 0,5 s sin órdenes, §15).
Capturas: `scripts/captura_aislada.sh` abre Gazebo y RViz2 cada uno en su Xephyr (:6/:5) y captura solo ese display; no se capturó el escritorio. Una primera captura de RViz2 se tomó con el robot bloqueado (odometría desfasada) y **se borró** para no confundir.

## 13. Incidencias del proceso (para que se sepa qué pasó)
- Dos veces quedaron **sistemas de simulación solapados** (procesos míos de una prueba anterior que mi cierre no mató): contaminaron una tanda de movimiento y la primera auditoría TF. Resultados descartados y repetidos con un solo Gazebo; añadido el control de «ya hay una simulación». Uno de mis intentos de limpiar por patrón de nombre fue **denegado** por el sistema de permisos; limpié solo por grupos de proceso que yo había creado.
- El `exec` de scripts auxiliares falló una vez por `__file__` (corregido). Ningún archivo de F0–F4 se editó.
- 🔎 No se probó la NVIDIA ni otra versión de ROS/Gazebo; no se probó con el robot ni el LiDAR reales.

## 14. Archivos nuevos
`urdf/tracer_agv.urdf.xacro` (+ `tracer_agv_rviz.urdf`), `modelos/tracer_agv/` (SDF, URDF de Gazebo, `chasis_colision.obj`, enlaces a las mallas de F0), `config/{bridge,inicio}.yaml`, `mundo/{vacio,piso_amueblado_tracer,piso_amueblado_tracer_gt}.sdf` (los dos últimos generados), `launch/tracer_piso.launch.py`, `rviz/tracer_piso{,_zoom}.rviz`, `scripts/` (`generar_robot.sh`, `generar_colision.py`, `generar_mundo.py`, `demo*.sh`, `parar_demo.sh`, `teleop.sh`, `arrancar_sin_gui.sh`, `lanzar_pruebas.sh`, `prueba_{movimiento,colision,lidar}.py`, `comprobar_tf.py`, `barrido_mapa.py`, `huella_libre.py`, `medir_*.py|sh`, `captura_aislada.sh`, `puente_verdad.sh`), `logs/`, `evidencias/capturas/`.

## 15. Ampliación: parada automática (watchdog de `/cmd_vel`)
**Motivo:** `DiffDrive` conservaba la última orden. **Verificación previa:** `strings libgz-sim-diff-drive-system.so` (gz-sim 8.15.0) solo muestra `min/max_acceleration`, `max_jerk`, `odom_publish_frequency`; **no existe parámetro de timeout** → no se podía configurar, hacía falta un watchdog.
**Diseño** (`scripts/watchdog_cmd_vel.py`): suscribe `/cmd_vel` (usuario) y publica **siempre** a 50 Hz en `/cmd_vel_seguro`: la última orden si tiene ≤ 0,5 s (**tiempo de simulación**, para que valga con RTF ≠ 1), o cero. Descarta mensajes con valores no finitos. Al cerrarse con Ctrl+C publica un cero final. El **0,5 s** es el valor pedido: es mayor que el periodo de órdenes de 10–30 Hz, y a 0,3 m/s la parada ocurre a < 17 cm (a 0,2 m/s, la velocidad de la demo, ~11 cm); un timeout menor (p. ej. 0,2 s) daría paradas falsas con retardos del puente o con el retardo inicial de repetición del teclado.
**Que no pueda evitarse:** `DiffDrive` escucha `/cmd_vel_seguro` (URDF/SDF regenerados con `generar_robot.sh`); `config/bridge.yaml` **ya no puentea `/cmd_vel`**; `launch/tracer_piso.launch.py` y `lanzar_pruebas.sh` arrancan el watchdog. Ningún script de F5 publica en `/cmd_vel_seguro`. Comprobación: `gz topic -t /cmd_vel -m gz.msgs.Twist -p 'linear: {x: 0.3}'` (el tópico de Gazebo antiguo) deja el robot en x = −6·10⁻⁵ m tras 2 s. Quien publique a propósito en `/cmd_vel_seguro` (ROS) o en Gazebo con `gz topic` sí lo evita; no es un cerrojo, es una protección contra olvidos.
**Pruebas** (`scripts/prueba_parada.py` → `logs/parada.json`, `logs/parada.txt`; 0,3 m/s; mundo `piso_amueblado` con verdad de terreno; sistema recién arrancado; ejecutadas una vez):
| | Orden / evento | Última orden (t sim) | Watchdog → cero | Parada | Velocidad real en la última orden → final | Desplazamiento hasta parar / después | Estado del controlador al final | Resultado |
|---|---|---|---|---|---|---|---|---|
| A | teleop real, `i` ×40 a 20 Hz, SIGKILL, sin `k` | 72,493 s | 0,507 s | 0,557 s | 0,300 → 0,000 m/s | 0,158 m / 0 | `/cmd_vel_seguro` = 0 y publicando | ✅ |
| B1 | teleop real, Ctrl+C (`\x03` por el pty) | 85,744 s | 0,001 s* | 0,006 s | 0,000 → 0,000 | 0 / 0 | idem | ✅ (*la «última orden» fue el cero que publica el propio teleop al salir: **no ejercitó el watchdog**) |
| B2 | `ros2 topic pub -r 10`, SIGINT | 98,475 s | 0,505 s | 0,555 s | 0,300 → 0,000 | 0,158 m / 0 | idem | ✅ |
| C | 10 Hz × 2 s, silencio sin cero | 107,445 s | 0,515 s | 0,565 s | 0,300 → 0,000 | 0,161 m / 0 | idem | ✅ |
| D | contra `caja_1` (bloqueado, v real 0), silencio, caja retirada con `gz service …/remove`, 5 s | 133,745 s | 0,515 s | ya parado (0,005 s) | 0,000 → 0,000 (máx. 0,000 tras retirar la caja) | 0 / 0,000 m | idem | ✅ no reanuda |
| E | orden válida 0,3 m/s × 4 s tras caducidad | — | — | — | odom 0,300 m/s | recorre 1,189 m (esperado 1,200) | sigue la orden | ✅ reanuda |
**Tiempo máximo de parada: 0,565 s** (prueba C). Descomposición: 0,50–0,52 s de timeout + ~0,05 s de respuesta de la rueda; ~0,16 m a 0,3 m/s. La misma prueba del `lanzar_pruebas.sh` previo (sin watchdog) habría seguido indefinidamente (observado en la sesión anterior; no se repitió a propósito).
**Limitaciones de estas pruebas:** una ejecución por escenario; D usa la caja (se retiró del mundo **en memoria**, F4 intacto); B1 no mide el watchdog (ver arriba); no se probó la muerte del propio watchdog (el robot conservaría la última orden) ni órdenes < 2 Hz (el robot avanzaría a tirones); `teleop_twist_keyboard` solo publica mientras se repite una tecla.
**Regresión** (`logs/mov_regresion_watchdog.json/.txt`, pruebas A y B, mundo `piso_amueblado`, robot en (0,0)): avance idéntico (0,1/0,3/0,6/1,0/1,5 m/s: Gazebo 0,3984/1,1919/2,3742/1,9367/2,8647 m frente a 0,3984/1,1916/2,3742/1,9353/2,8647 m antes; atrás −1,1895 igual); giro 90° a 0,2/0,5/1,0/1,5 rad/s: 89,79°/89,09°/87,66°/85,11° (antes 89,90°/89,52°/88,41°/87,00°), derecha −89,37° (antes −89,49°). Diferencias ≤ 1,9°, solo con ω ≥ 1,0 rad/s: **posible** latencia añadida por el watchdog (hasta 20 ms); no aislada. Parámetros físicos intactos. Las pruebas C, D y E de movimiento, colisiones, LiDAR y TF **no se repitieron**: no dependen del camino de `/cmd_vel` (el modelo solo cambió el nombre del tópico de entrada).
**Demo:** 4.º arranque desde cero (`scripts/demo.sh`) con watchdog: 8 nodos (incl. `watchdog_cmd_vel`), orden `ros2 topic pub -r 10 --times 20 /cmd_vel {x: 0.2}` → odometría avanza 0,523 m (2 s de orden + 0,5 s de espera) y 3 s después sigue en 0,5234; `/cmd_vel_seguro` = 0; `parar_demo.sh` → 0 procesos residuales.
**Odometría (sin cambios):** real 1,56 m, odometría 4,1 m, diferencia **2,54 m** (RESUMEN §8). La odometría integra el giro de las ruedas y no es una referencia externa; diverge si las ruedas giran contra un obstáculo. No se corrige artificialmente.
**Velocidades de la demo:** `teleop.sh` 0,2 m/s y 0,5 rad/s (error medido < 1 % y ≤ 0,6°). Las pruebas a 1,0 y 1,5 m/s se conservan como evidencia, **sin presentarlas como validadas** con la precisión de 0,3 m/s.
**Archivos modificados/nuevos en esta ampliación:** nuevos `scripts/watchdog_cmd_vel.py`, `scripts/prueba_parada.py`, `logs/parada.{json,txt}`, `logs/mov_regresion_watchdog.{json,txt}`; modificados `urdf/tracer_agv.urdf.xacro` (+ regenerados `modelos/tracer_agv/{model.sdf,tracer_agv_gz.urdf}`; `urdf/tracer_agv_rviz.urdf` sin cambios de contenido), `config/bridge.yaml`, `launch/tracer_piso.launch.py`, `scripts/lanzar_pruebas.sh`, `scripts/teleop.sh`, `scripts/demo.sh` (solo mensaje), `RESUMEN F5.md`, este anexo. Las evidencias y logs anteriores se conservan. **Limitaciones aceptadas** (sin cambios, documentadas en RESUMEN y §2–§11): dimensiones sin confirmar, masas/inercias/fricciones estimadas, LiDAR físico sin confirmar, tracer2 2025 frente al original, base de silla estimada, visibilidad del LiDAR por altura, ruedas motrices esféricas, 1 kHz en `/clock`/`/joint_states`, licencias de mallas. El modelo es una aproximación de simulación, no una validación física del TRACER real.

## 16. Cierre documental (2026-11-09)
**F5 — CERRADA Y VALIDADA EN SIMULACIÓN, CON LIMITACIONES DOCUMENTADAS.** Autorizado por José Ángel tras revisar la ampliación del watchdog (§15). Esta validación **no implica equivalencia demostrada con el comportamiento del TRACER AGV físico**.
- **Watchdog:** aceptado con timeout de 0,5 s y parada máxima observada de 0,565 s. **No es un sistema de parada de seguridad ni un fail-safe**: si el nodo `watchdog_cmd_vel` termina, `DiffDrive` puede conservar la última orden. Aceptado solo para simulación; **no usar como protección de un robot físico**; no se declara parada de emergencia certificada.
- **Limitaciones aceptadas** (lista completa en `RESUMEN F5.md` §9; detalle en §2–§11 y §15): parámetros físicos estimados; esferas en ruedas motrices; tracer2 2025 frente al original; odometría con el robot bloqueado (1,56 m real, 4,1 m odometría, +2,54 m); colisiones simplificadas del mobiliario; LiDAR físico sin confirmar; licencias de mallas; frecuencias de 1 kHz; hasta 1,9° extra en giros rápidos; tirones con órdenes lentas; watchdog probado una vez por escenario; sin parada garantizada si muere el watchdog.
- **Sin cambios:** en el cierre no se repitieron pruebas ni se modificó ningún archivo funcional (solo `RESUMEN F5.md`, este anexo y `evidencias/ARCHIVOS PARA F6.md`). Todos los logs, mediciones y capturas anteriores se conservan.
- **Reproducción:** `cd "…/F5_INTEGRACION_TRACER" && scripts/demo.sh` / `scripts/teleop.sh` / `scripts/parar_demo.sh`.
