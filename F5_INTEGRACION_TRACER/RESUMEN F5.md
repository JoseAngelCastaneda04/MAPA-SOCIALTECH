# RESUMEN F5 — AgileX TRACER AGV simulado en el piso amueblado (Gazebo Harmonic + ROS 2 Jazzy + RViz2)

**Estado: F5 — CERRADA Y VALIDADA EN SIMULACIÓN, CON LIMITACIONES DOCUMENTADAS** (cierre autorizado por ti el 2026-11-09; no se repitieron pruebas). **Esta validación no implica equivalencia demostrada con el comportamiento del TRACER AGV físico.** F6 no iniciada, a la espera de tu autorización · **Para F6:** `evidencias/ARCHIVOS PARA F6.md` · F0–F4 no modificadas (sus archivos siguen con fecha del 2026-11-07/08; el mundo de F4 conserva su MD5) · **Anexo:** `evidencias/DETALLE F5.md`
Leyenda: ✅ medido/ejecutado · ⚠️ funciona con condiciones · 🔎 no comprobado. Rutas relativas a `F5_INTEGRACION_TRACER/`. Todo es **simulación**; no se tocó el robot real, CAN ni la Jetson.

## 1. Conclusión
El TRACER AGV (modelo original, no 2.0) carga en el apartamento de F4, se mueve con `/cmd_vel`, publica `/odom`, `/tf`, `/joint_states` y `/scan`, y RViz2 lo dibuja sobre el mapa de F4. Tiene **un solo publicador por transformación**, y las pruebas de movimiento y colisión se contrastaron con la **pose real de Gazebo**, no solo con la odometría. Hubo **dos errores míos** que las mediciones destaparon y se corrigieron (§4). Las limitaciones están en §8.

## 2. Qué modelo es (y qué no)
- **AgileX TRACER AGV original**, geometría de `agilexrobotics/tracer_ros` (copia de F0, commit `774ba0f`, ROS 1). Mallas de F0 **referenciadas por enlace simbólico**, sin copiarlas.
- **No hay una versión lista para Jazzy + Harmonic**: `tracer_ros2` (Apache-2.0, rama `humble`) solo trae `tracer_base`/`tracer_msgs`, sin descripción ni simulación; `ugv_gazebo_sim/tracer` es ROS 1/Melodic + Gazebo Classic (y trae también `tracer2_description`, el 2.0). Se **portó**: xacro propio → URDF (RViz2) y SDF (Gazebo) con `gz-sim-diff-drive-system`, `joint-state-publisher` y `gpu_lidar`.
- **El «tracer2» de SocialTech 2025 es un híbrido, no un Tracer 2.0 demostrado**: chasis 0,685 × 0,57 m (como el original), ruedas Ø 0,125 m (como el 2.0), separación 0,26 m en el URDF frente a 0,335 m en su plugin (el original: 0,34 m), 42,9 kg. No se mezcló con nuestro modelo.
- **Medido en las mallas oficiales** ✅: chasis 0,685 × 0,570 m, ruedas motrices Ø 0,121 × 0,0844 m a y = ±0,17 m (separación 0,34 m), ruedas locas Ø 0,0744 m, altura total 0,1645 m, holgura al suelo 34,5 mm. **Documentado**: 30 kg, 1,6 m/s, holgura 30 mm. **Estimado** (no documentado): reparto de masas e inercias, fricciones, centro de gravedad. **Fuentes en conflicto**: dimensiones 660 × 516 × 163,5 (Trossen) frente a 685 × 570 × 155 (Robosavvy); vía 0,36 m (Robosavvy) frente a 0,34 m (URDF). Detalle y licencias en el anexo (§1–§3).
- 🔎 **Licencias:** `tracer_ros` y `ugv_gazebo_sim` **no traen archivo LICENSE** (el `package.xml` dice BSD en casi todo y `TODO` en la descripción). Uso solo local; **no redistribuir las mallas** sin preguntar a AgileX.

## 3. Frames, TF y coordenadas ✅
`map →(estático) odom →(Gazebo DiffDrive, 50 Hz) base_footprint →(rsp) base_link → {laser, ruedas, ruedas locas}`.
- `map→odom` **no es identidad**: es la pose inicial (9,70; −2,70; −90°) de `config/inicio.yaml` (única fuente: mundo y TF); `odom` nace ahí. Sin AMCL: si el robot se desliza, `odom` deriva (§8).
- Auditoría de 30 s con el robot en movimiento: **0** hijos con varios padres, **0** fallos de búsqueda (23 834), **0** extrapolaciones, sellos en tiempo de simulación (retraso mediano 0 s). `map→base_footprint` frente a la pose real de Gazebo: **0,9 mm** de media (máx. 1,1 mm), 0,37° de yaw (máx. 0,58°; es la deriva normal de la odometría al girar).
- Mundo (Gazebo) = mapa = CAD: sin desplazamiento (F3/F4). Ya no hay `map→world` (F4 lo usaba; en F5 no hace falta).

## 3b. Parada automática (añadida tras tu revisión) ✅
- **Verificado:** el `DiffDrive` de gz-sim 8.15 **no tiene timeout** (su binario solo expone aceleración/jerk). Solución mínima: `scripts/watchdog_cmd_vel.py` (~40 líneas, `rclpy`, tiempo de simulación): `/cmd_vel` → watchdog → `/cmd_vel_seguro` (50 Hz, siempre publica) → puente → `DiffDrive`. Si la última orden tiene > **0,5 s**, publica velocidad cero; una orden caducada **nunca** se reenvía. `/cmd_vel` ya **no** se puentea: ningún script de F5 llega al `DiffDrive` sin pasar por el watchdog. Comprobado: publicar directamente al tópico antiguo de Gazebo `/cmd_vel` no mueve el robot (solo se podría saltar publicando a propósito con `gz topic` a `/cmd_vel_seguro`).
- **Pruebas** (`scripts/prueba_parada.py`, `logs/parada.json`, a 0,3 m/s, tiempos de simulación desde la última orden; parada = |v| < 0,01 m/s sostenida):
| | Prueba | Watchdog → cero | Parada real | Desplazamiento hasta parar | Resultado |
|---|---|---|---|---|---|
| A | `teleop_twist_keyboard` real (tecla `i` 2 s), proceso **muerto con SIGKILL** sin `k` | 0,507 s | 0,557 s | 0,158 m | ✅ para |
| B1 | teleop real + **Ctrl+C** | — | 0,006 s | 0 m | ✅ para, pero **aquí paró el propio teleop** (publica un cero al salir): el watchdog no se ejerció |
| B2 | `ros2 topic pub -r 10` + **Ctrl+C** (SIGINT) | 0,505 s | 0,555 s | 0,158 m | ✅ para |
| C | 10 Hz durante 2 s y **silencio** | 0,515 s | 0,565 s | 0,161 m | ✅ para |
| D | empujando contra `caja_1` (bloqueado), se deja de publicar, se **retira la caja** y se esperan 5 s | 0,515 s | ya parado | **0,000 m** tras retirarla (v máx 0) | ✅ no reanuda |
| E | orden válida tras una caducidad (0,3 m/s × 4 s) | — | — | recorre 1,189 m (esperado 1,200; antes del watchdog −8,4 mm, ahora −11,0 mm) | ✅ reanuda |
- **Tiempo máximo de parada observado: 0,565 s** tras la última orden (0,515 s del watchdog + ~0,05 s de la rueda), con **16,1 cm** recorridos a 0,3 m/s. No se desplaza nada tras parar (< 1 µm).
- **Regresión de movimiento** (pruebas A y B de nuevo, `logs/mov_regresion_watchdog.json`): el avance es **idéntico** (0,3 m/s: −8,1 mm frente a −8,4 mm; 1,5 m/s: −135 mm igual). El giro de 90° cambia algo con ω alto: 1,0 rad/s 87,66° (antes 88,41°); 1,5 rad/s 85,11° (antes 87,00°; ≤ 0,3° a ω ≤ 0,5). **Posible** causa: el watchdog añade hasta ~20 ms de latencia; no la aislé (también cambió el mundo de prueba). No se tocó ningún parámetro físico.
- ⚠️ Limitación: una orden publicada a menos de 2 Hz parpadea (se para entre mensajes); con `teleop` hay que mantener la tecla (la repetición del teclado ya publica a ~20–30 Hz, aunque el retardo inicial de repetición del sistema puede acercarse a los 0,5 s).

## 4. Dos errores míos corregidos (por las mediciones)
1. **Ruedas locas 9 cm demasiado altas** (error de cuenta en el xacro) → el robot quedaba inclinado 6,7°. Corregido; en reposo: z = 0,000 m, cabeceo −0,057° (los 0,2 mm de diferencia entre las alturas del fabricante).
2. **Giro al 80 %**: con ruedas de colisión cilíndricas el robot giraba 72° cuando la odometría decía 90° (proporción constante 0,17/0,212 = contacto por el borde exterior). Las ruedas motrices usan ahora **colisión esférica** (r = 0,0605 m, contacto en la línea central): 89,9°. **Es una simplificación**, documentada.

## 5. Movimiento (mundo vacío, referencia = pose real de Gazebo) ✅
**Intervalo con buen comportamiento y usado en la demo (teleop 0,2 m/s, 0,5 rad/s):** avance ≤ 0,6 m/s con error ≤ 1,1 % y giro ≤ 0,5 rad/s con error ≤ 0,6°. **La prueba a 1,0–1,5 m/s NO está validada con la misma precisión** (−65/−135 mm, escalón de velocidad sin límite de aceleración; la odometría sobreestima +43/+104 mm); no se ajustó ningún parámetro para mejorarla.
| Prueba | Resultado (Gazebo − esperado) |
|---|---|
| A avance 0,1 / 0,3 / 0,6 m/s | −1,6 / −8,4 / −25,8 mm (0,4 %–1,1 %); lateral 0 |
| A avance 1,0 / 1,5 m/s (aceleración sin límite) | −65 / −135 mm; la odometría sobreestima +43 / +104 mm |
| B giro 90° a 0,2 / 0,5 / 1,0 / 1,5 rad/s | −0,10° / −0,50° / −1,61° / −3,07° |
| C parada (tras 0,3 y 1,0 m/s) | desliza 7 / 63 mm más tras `v=0` (rampa de la rueda) |
| D combinado (4 casos) | error de posición ≤ 0,07 m y de yaw ≤ 4,7° (peor: v=0,8, ω=0,8) |
| E cuadrado de 1 m ×3 | las tres repeticiones terminan a **0,09 mm** del inicio (simulación determinista) |
No se fijaron márgenes de error: todas las cifras están en el anexo, con `logs/mov_vacio.json`.

## 6. En el apartamento ✅
- **Inicio** (9,70; −2,70; −90°): la **huella completa** (polígono del chasis + ruedas, orientado) cae en libre; holgura 0,45 m; cabe el giro sobre sí mismo (radio circunscrito 0,381 m, libre hasta 0,77 m). Nada de F4 se movió.
- **Colisiones a 0,3 m/s** (parada real frente a la prevista barriendo la huella por el mapa): pared −2,5 mm · mesa_1 −6,6 mm · caja +7,5 mm · silla_E (costado) −1,6 mm · silla_N **+38 mm** · puerta de 1,01 m ✅ **pasa** · puerta de 0,91 m ✅ **pasa** (para en el muro posterior, −10 mm). Sin trepar (z ≤ 2 mm, cabeceo ≤ 0,16°).
- **LiDAR de prueba** (gpu_lidar, marco `laser`, 0,20 m sobre el suelo, 360°, 720 haces, 0,1–30 m, 10,0 Hz medidos, sin ruido): error mediano **2–5 mm** frente al trazado de rayos sobre el mapa. **No ve las sillas** (a 0,20 m solo hay patas finas): en las poses del salón, 50–80 de 720 haces cruzan donde el mapa dice «silla». Tampoco ve tableros ni asientos. Los **puntos del LiDAR dibujados por RViz2** caen a ≤ 2 cm de celdas ocupadas (250 de 250; medido sobre píxeles, 110 px/m).
- **Banda del mapa (0,05–1,8 m) no cambiada**; coherente con las colisiones (el robot sí choca con lo que el mapa marca), pero el LiDAR a 0,20 m ve menos que el mapa.

## 7. Rendimiento y demostración
Servidor Gazebo (headless, 15 s, medido igual en los tres): F4 **183 MB / 26 % CPU**; + TRACER sin lidar **197 MB / 54 %**; + lidar **496 MB / 58 %**; carga 4,5 s (igual que F4); factor de tiempo real **0,999**. Con GUI real + RViz2: servidor 487 MB / 93 %, GUI 627 MB / 130 %, RViz2 331 MB / 43–49 % (en F4: 192 MB / 3 %). `/odom` 50,0 Hz, `/scan` 10,0 Hz, `/tf` 70 Hz, pero `/clock` y `/joint_states` salen a **1 000 Hz** (el puente consume ~31–37 % de CPU). Arranque desde cero **4 veces** (la 4.ª, con el watchdog: orden de 2 s → avanza 0,52 m y se queda parado), cierre sin procesos residuales (grupos de procesos, sin `pkill`):
```bash
cd "/home/jose-angel/Desktop/MAPA SOCIALTECH/F5_INTEGRACION_TRACER"
scripts/demo.sh            # Gazebo + puente + TF + mapa + RViz2   (Ctrl+C o scripts/parar_demo.sh cierra todo)
scripts/teleop.sh          # en otra terminal: teclado (i , j l; k = parar; mantén la tecla: sin órdenes 0,5 s = parada automática)
```

## 8. Limitaciones y avisos (aceptadas en el cierre)
- ⚠️ **Odometría ≠ referencia externa de posición.** Contra un obstáculo las ruedas siguen girando y la odometría acumula distancia falsa: **real 1,56 m, odometría 4,1 m, diferencia 2,54 m** (medido empujando contra una silla). No se corrigió artificialmente; la localización futura (F6+: AMCL/SLAM, no hecha) debe abordarlo. La parada automática (§3b) limita cuánto dura ese empuje, pero no corrige la odometría.
- ⚠️ Con el watchdog el robot ya no continúa sin órdenes; el `DiffDrive` sigue sin timeout propio y el watchdog es un nodo ROS: si **él** muere, el robot conserva la última orden (no lo probé).
- ⚠️ Simplificaciones: ruedas locas **fijas** con fricción 0,02 (el fabricante las modela con 2 articulaciones); ruedas motrices **esféricas**; colisión del chasis = casco convexo simplificado (error ≤ 5,2 mm). 🔎 Masas, inercias y fricciones **estimadas**; el comportamiento dinámico (aceleraciones, patinaje) no es el del robot real.
- ⚠️ **Sillas:** la base sigue siendo la **estimación de F4** (cilindro r 0,25 × 0,04 m). El choque lateral con `silla_E` solo prueba que ese cilindro bloquea al chasis (su parte baja está a 34 mm); **no valida la silla real**. Con la malla porosa original se atravesaría. No se cambió ninguna geometría de F4.
- 🔎 Frente = +X **supuesto** (las mallas son casi simétricas). Posición del LiDAR/sensores del equipo actual: **sin confirmar** (2025: `rslidar` a 0,2125/0/0,20 m, pero el plugin lo llamaba «hokuyo»; también había cámara e IMU, no integradas). Sin ruido en el LiDAR.
- 🔎 La RAM/CPU de RViz2 y el puente subieron respecto a F4; el coste del puente por `/clock`+`/joint_states` a 1 kHz está medido, no optimizado. Las capturas se hicieron en displays aislados (Xephyr, Mesa software), así que **no** se usaron para rendimiento.
- Avisos en logs: «`gz_frame_id` no definido en SDF» (sdformat lo copia y funciona), `libEGL warning` del driver y el GLSL de RViz2 ya conocido de F3. 0 errores de Gazebo.
- Los resultados son de simulación; **no validan el robot físico**.

## 9. Cierre (2026-11-09)
Aprobado por ti: integración del TRACER AGV original en Gazebo Harmonic; comunicación con ROS 2 Jazzy; movimiento por `/cmd_vel`; odometría y TF; LiDAR simulado; colisiones con paredes, puertas y mobiliario; RViz2; demostración reproducible; watchdog (timeout 0,5 s, parada máxima observada 0,565 s).
**⚠️ El watchdog NO es un sistema de parada de seguridad.** Es una comodidad de simulación: si el propio watchdog muere, `DiffDrive` conserva la última orden. **No debe usarse como mecanismo de seguridad de un robot físico**, y **no** se declara parada de emergencia certificada ni sistema fail-safe.
**Limitaciones aceptadas, sin resolver** (se retomarán solo si importan a fases posteriores): parámetros físicos estimados (masas, inercias, fricciones, CdG) y dimensiones sin confirmar; ruedas motrices esféricas y ruedas locas fijas; discrepancias del antiguo «tracer2» de 2025 con el TRACER original; odometría que diverge con el robot bloqueado (1,56 m reales frente a 4,1 m, +2,54 m) y no es referencia externa; colisiones simplificadas del mobiliario (base de silla estimada); LiDAR físico sin confirmar y visibilidad distinta según su altura; licencias de las mallas del fabricante sin aclarar (no redistribuir); `/clock` y `/joint_states` a 1 kHz y coste de RViz2/puente; hasta 1,9° de desviación adicional en giros rápidos (ω ≥ 1,0 rad/s); avance a tirones con órdenes a < 2 Hz; pruebas del watchdog hechas **una vez** por escenario; sin parada garantizada si muere el watchdog.
**Conservado y reproducible** (`scripts/demo.sh`, `scripts/parar_demo.sh`, `scripts/teleop.sh`): modelo del TRACER, mundo amueblado, mapa de F4, configuración ROS 2, TF, LiDAR, watchdog y RViz2. Sin cambios funcionales ni pruebas nuevas desde la aprobación; no se eliminó ninguna evidencia.

## 10. Evidencias
`evidencias/DETALLE F5.md` · `evidencias/capturas/01_gazebo_tracer_piso.png`, `03_rviz_zoom_lidar.png` (solo displays aislados) · `logs/*.json` · `modelos/tracer_agv/`, `urdf/`, `mundo/`, `launch/`, `rviz/`, `scripts/`.
**F5 sigue abierta: no cierro ni paso a F6 sin tu autorización.**
