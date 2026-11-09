# Archivos y componentes de F0–F4 que F5 (integración del Tracer) puede reutilizar
F5 **no se ha iniciado**. Rutas relativas a `MAPA SOCIALTECH/`. Todo lo de F0–F4 es de solo lectura: copiar a `F5_INTEGRACION_TRACER/`, no editar.

## 1. Escenario y mapa (F4, listo)
| Para qué | Archivo | Notas |
|---|---|---|
| Mundo amueblado | `F4/mundo/piso_amueblado.sdf` | Generado; no editar a mano. Necesita `GZ_SIM_RESOURCE_PATH`/`SDF_PATH` = `F4/modelos:F2/mundo/modelos` (ver `F4/scripts/demo_gazebo.sh`) |
| Mapa para Nav2/RViz2 | `F4/mapa/piso_amueblado.{pgm,yaml}` | 0,01 m/celda, origen (4,7299; −11,32), mismo que F3; incluye mobiliario |
| Cambiar la distribución | `F4/config/mobiliario.yaml` + `F4/scripts/regenerar.sh` (`mobiliario.py anadir/mover/quitar`) | El robot no debe ir en este YAML; añadirlo en un mundo/launch de F5 |
| Demo y cierre | `F4/scripts/{demo,demo_gazebo,parar_demo}.sh`, `F4/launch/mapa_rviz.launch.py`, `F4/config/piso_amueblado.rviz` | Cierre por grupo de procesos, sin `pkill` |
| Medidas/capturas seguras | `F4/scripts/{rviz_aislado.sh,medir_rviz_mobiliario.py,comparar_gazebo_rviz.py,comprobar_mapa.py}` | Capturas: usar Xephyr o recortar; no capturar el escritorio del usuario |
| Pruebas físicas | `F4/scripts/prueba_colisiones.py` | Plantilla para probar el robot contra los muebles (bolas dinámicas + `VelocityControl`) |

## 2. Robot Tracer (F0, ROS 1: hay que portar)
| Qué | Dónde | Estado |
|---|---|---|
| Robot de 2025 `tracer2` | `F0/SocialTech-Gazebo/urdf/{tracer2.xacro,tracer2.gazebo,lidar.xacro,camera.xacro,imu.xacro,materials.xacro}` | Plugins de **Gazebo Classic** (`libgazebo_ros_diff_drive`, `_laser`, `_camera`, `_imu_sensor`): no valen en Harmonic; sustituir por `gz-sim-diff-drive-system`, `gpu_lidar`, etc. (`ros_gz_bridge`) |
| Lidar 2025 | `lidar.xacro`: `rslidar_link` en (0,2125; 0; 0,20) m sobre la base | **0,20 m** cae dentro de la banda del mapa (0,05–1,8 m): comprobar con el lidar real (limitación 4 de F4) |
| Descripción del fabricante | `F0/tracer_ros/tracer_description/{urdf,meshes,rviz}` (mallas `.dae`/`.stl`), `tracer_gazebo_sim`, `tracer_base`, `tracer_msgs` | Copias de AgileX (commit `774ba0f`) de ROS 1; solo se reutilizan mallas/dimensiones. No ejecutado nada aún |
| Variante exacta del Tracer | **Pendiente de definir** (heredado de F0) | Preguntar a IQS cuál es antes de elegir modelo |
| RViz 2025 | `F0/SocialTech-Gazebo/rviz/model_display.rviz` | RViz 1; la config de F4 ya está en RViz2 |

## 3. Qué hay que decidir/hacer en F5 (heredado de F0–F4)
- **TF:** hoy solo `map→world` identidad (F3). F5 necesita `map→odom→base_link` (+ sensores); revisar quién publica `odom`.
- **Origen/coordenadas:** mundo y mapa comparten coordenadas del CAD; posición inicial del robot debe darse en ellas y en libre (p. ej. zona libre x 9–10,5, y −3,3…−2 del salón, o la entrada oeste (5,09; −3,1) de ancho 1,54 m).
- **Banda z del mapa** y altura del lidar (F4, limitación 4). Si cambia: `slice_z` en `mobiliario.yaml` + `regenerar.sh`.
- **Colisión de la silla:** base estimada y prueba lateral no validada (limitaciones 1–2): el robot es el primer test real; con un Tracer bajo (< 0,1 m) la base de la silla importa.
- **Baranda abierta de la zona técnica y entrada oeste sin pasillo** (F2 §6): revisar antes de navegar.
- **Rendimiento:** usar la silla de colisión simple (`silla`); `silla_malla` cuesta +0,8 s y +230 MB. Un lidar de GPU en Gazebo no se ha medido.
- Herramientas ya instaladas (sin instalar nada): ROS 2 Jazzy, Gazebo Sim 8, RViz2, `nav2_map_server`; **no comprobado** si hay `ros_gz_bridge`, `nav2_bringup`, `slam_toolbox`, `robot_localization` (verificar con `ros2 pkg list` al empezar F5).
- Restricción vigente: no navegación autónoma ni checkpoints salvo que el responsable lo autorice.

## 4. Lecciones de F4 aplicables
`<include><pose>` sustituye la pose del modelo; origen en esquina en mesas; `gz sdf -k` resuelve `model://` con `SDF_PATH`; esperar al tiempo de simulación (`/world/<w>/stats`), no al reloj; `VelocityControl` impone la velocidad cada paso; no `pkill -f`; rutas con espacio: entrecomillar siempre.
