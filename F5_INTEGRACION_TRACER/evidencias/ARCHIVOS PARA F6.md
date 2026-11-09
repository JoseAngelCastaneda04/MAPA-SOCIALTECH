# Archivos y procedimiento para F6 (plano real de IQS)
**F6 no se ha iniciado** y `F6_PLANO_REAL_IQS/` está vacía. No hay plano de IQS: **no se asume ninguna dimensión, orientación ni distribución del espacio real.** Rutas relativas a `MAPA SOCIALTECH/`. Todo lo de F0–F5 es de solo lectura: se copia a `F6_PLANO_REAL_IQS/` y se edita la copia. El apartamento de prueba (F2/F4/F5) no se toca.

## 1. Reutilizable de F1–F5
| Paso | Qué | Dónde | Notas |
|---|---|---|---|
| DWG → DXF | LibreDWG 0.14 (`dwg2dxf`) | `F1/herramientas/libredwg_gnu` (compilado con `F1/scripts/compilar_libredwg.sh`) | Avisos «Unstable Class» sin efecto (F2) |
| DXF → plano limpio | `ezdxf` (venv) + scripts de F2 | `F1/herramientas/venv`; `F2/scripts/recortar_piso.py` (aislar el plano), `cerrar_lazos.py` (líneas sueltas → lazos), `dxf_m_a_mm.py` (unidades) | **Específicos del DXF de DesignsCAD**: capas, ventana y tolerancias hay que reajustarlos |
| DXF → mapa nav2 | `F1/scripts/dxf_a_mapa.py` (`--unidades`, capa de muros, resolución) | F1 | Lee `$INSUNITS` (en F2 estaba mal: se forzó `--unidades 6`) |
| PDF/PNG → mapa | `F1/scripts/raster_a_mapa.py`, `corregir_perspectiva.py` | F1 | Solo vectorial con muros rellenos y de color propio, o con 1 cota de calibración |
| Mapa → modelo 3D | `map2sdf --format model --wall-height <h>` | `F1/ws/install` (`source F1/ws/install/setup.bash`) | **Resolución 0,02 o 0,01 m/celda** (a 0,025/0,04/0,05 m rellena el interior; causa sin analizar). Altura de muro = parámetro, no dato del plano |
| Mapa 2D con mobiliario | `sdf2map` (nube) + `F4/scripts/combinar_mapas.py` | F1/F4 | Usar la **nube** y unir a la rejilla del mapa base; no el mapa remuestreado de `sdf2map` (desplaza ±1 celda) |
| Mobiliario | `F4/scripts/{crear_modelos.py, mobiliario.py, generar_mundo.py, regenerar.sh}`, `F4/config/mobiliario.yaml` | F4 | Rutas **fijas a F2/F3** (`mapa_base`, `mundo_base`, `regenerar.sh`): al copiarlos a F6 hay que cambiarlas |
| Comprobar mapa | `F4/scripts/comprobar_mapa.py`, `F2/scripts/medir_cotas.py` + `cotas_verificadas.json` | F2/F4 | Necesitan **cotas del plano real** (puntos, ejes, valores) |
| RViz2 y mapa | `F3`/`F4` (`launch/mapa_rviz.launch.py`, `config/*.rviz`) | F3/F4 | |
| Robot y demo | **F5 completa**: `modelos/tracer_agv`, `urdf/`, `config/{bridge,inicio}.yaml`, `launch/tracer_piso.launch.py`, `scripts/watchdog_cmd_vel.py`, `scripts/{generar_robot,generar_mundo,demo,demo_gazebo,parar_demo,teleop,arrancar_sin_gui}.sh|py`, `rviz/` | F5 | Ver §6 |
| Medidas | `F5/scripts/{huella_libre,barrido_mapa,prueba_colision,prueba_lidar,comprobar_tf,medir_*}.py` | F5 | Huella libre, colisiones, LiDAR frente a mapa, TF |
| Capturas aisladas | `F5/scripts/captura_aislada.sh` (Xephyr) | F5 | Nunca capturar el escritorio |

## 2. Procedimiento recomendado (plano → TRACER)
1. **Recibir y registrar el plano** (formato, versión, fecha, SHA-256, licencia/permiso de uso). Guardar el original en `F6/original/` sin modificar ni redistribuir.
2. **Inspeccionar** (DXF: capas, `$INSUNITS`, extensión, entidades; PDF: vectorial o escaneado). Decidir unidades con **cotas conocidas**, no con la cabecera (F2 lo demostró).
3. **Aislar el espacio de la competición** (ventana y capas) y **cerrar los muros** en lazos (`cerrar_lazos.py`); anotar qué se descarta.
4. **Mapa 0,01–0,02 m/celda** con `dxf_a_mapa.py`; comprobar contra ≥ 6 cotas **medidas en el plano** (`medir_cotas.py`). Errores en metros, sin márgenes amplios.
5. **Modelo de muros** con `map2sdf` (altura real de la sala **si IQS la da**; si no, parámetro documentado) y mundo con suelo y luz; `gz sdf -k` y carga en Gazebo.
6. **Aberturas:** hueco abierto como en 2025 (decisión del responsable, F0). Medir cada hueco; las puertas de 2025 (`door`) solo si se decide incluirlas.
7. **Mobiliario y máquinas** (§5) → `mobiliario.yaml` → `regenerar.sh` (mundo + mapa).
8. **RViz2** (`map_server` + TF) y comparación Gazebo ↔ mapa (F3/F4).
9. **TRACER** (§6): pose inicial libre con huella completa, TF `map→odom`, LiDAR, demo, pruebas de colisión y huecos.
10. **Documentar** (`RESUMEN F6.md`, `evidencias/DETALLE F6.md`), mantener F0–F5 intactas; no cerrar sin autorización.

## 3. Formatos de entrada (por orden de preferencia, según F1/F2)
| Formato | Estado | Condición |
|---|---|---|
| **DXF** con capas y muros en contornos cerrados | ✅ sin pérdida | Indicar la capa de muros; unidades confirmadas |
| **DWG** | ✅ vía LibreDWG → DXF (comprobado con AutoCAD 2018 `AC1032`) | Versiones más nuevas o distintas: 🔎 no probado |
| PDF vectorial en color, muros rellenos | ⚠️ ±0,05 m | Escala de impresión o 1 cota |
| PDF monocromo / con muros en contorno | ❌ sin limpieza manual | Pedir DXF/DWG |
| PNG/JPG, escaneado | ⚠️ solo caso favorable simulado | Calibración con cota; enderezado; muros rellenos |
| Mapa nav2 (PGM/PNG + YAML) | ✅ directo a `map2sdf` | Origen y resolución conocidos |

## 4. Requisitos que debe cumplir el plano
- **Escala y unidades inequívocas** y **≥ 6 cotas** de control repartidas (incluidos pasillos, puertas y zona de competición) para medir errores.
- Muros en **capa propia**, como polilíneas **cerradas** (o líneas que `edgeminer` pueda cerrar); sin detalles de otras plantas mezclados.
- **Origen/ejes** identificables (el CAD en F2 los conservaba; un PDF los pierde).
- Aberturas (puertas, vanos, escaleras, ventanas) **dibujadas y acotadas**; indicar cuáles son transitables.
- Idealmente **altura útil, desniveles, rampas, columnas** y la **zona exacta de la competición** (checkpoints, líneas, límites).

## 5. Mobiliario y máquinas como modelos independientes
- **Estructura de 2025/F4:** un modelo SDF por tipo de objeto + `<include>` con nombre y pose en el mundo (x, y = centro de la huella, yaw), definido en `mobiliario.yaml`; el mundo y el mapa se regeneran de ahí.
- **Procedimiento:** (1) obtener la malla (OBJ/STL/DAE) y **medir** dimensiones y origen (`F4/scripts/medir_malla.py`); (2) crear el modelo con origen en el centro de la huella y z = 0 en el suelo (`crear_modelos.py`; los orígenes de las mallas de 2025 estaban en la esquina o con doble giro: F4 §2); (3) **colisión explícita**: primitivas medidas (cajas/cilindros) o malla convexa simplificada como en `F5/scripts/generar_colision.py`; la malla de 155 k triángulos como colisión cuesta +0,8 s y +230 MB; **los OBJ de colisión necesitan normales** (dartsim aborta si faltan); (4) `mobiliario.py anadir|mover|quitar` + `regenerar.sh`; (5) comprobar huellas en el mapa y bolas/colisión.
- **Máquinas:** igual, con sus dimensiones **reales** (pedir ficha o CAD). Hay que decidir si son **estáticas** (`<static>`) o dinámicas, y su altura frente a la banda del mapa.
- No se admiten obstáculos móviles/aleatorios (decisión de F0). Los checkpoints y elementos de competición corresponden a **F7**.

## 6. Reutilizar el TRACER AGV en el nuevo escenario
- Copiar `F5/{modelos,urdf,config,launch,rviz,scripts}` a `F6` (o referenciar con `GZ_SIM_RESOURCE_PATH`). **Las mallas son enlaces simbólicos a F0**; sin LICENSE → no redistribuir.
- Cambiar solo: **mundo** (`generar_mundo.py` lee el mundo de F4; apuntarlo al de F6), **mapa** (`launch`), **pose inicial** (`config/inicio.yaml`; `map→odom` se deriva de ella) y el nombre del mundo en las pruebas (`piso_amueblado`).
- Elegir la pose inicial con `huella_libre.py check x y yaw` (huella completa, giro sobre sí mismo) **en el mapa nuevo**, y revisar huecos y pasillos con `barrido_mapa.py` antes de mover el robot.
- El **watchdog** (0,5 s) sigue siendo una comodidad de simulación, **no** una parada de seguridad.

## 7. Limitaciones conocidas que pueden afectar al entorno real
- **TRACER:** dimensiones sin confirmar (660×516 frente a 685×570 según fuente), masas/inercias/fricciones estimadas, ruedas motrices esféricas, ruedas locas fijas, frente = +X supuesto, respuesta dinámica no validada. Simulación ≠ robot físico.
- **LiDAR:** sensor, altura (0,20 m copiada de 2025) y parámetros del equipo actual **sin confirmar**; a 0,20 m **no ve sillas, tableros ni asientos** pero el mapa y las colisiones sí los tienen. Decidir la banda de alturas del mapa (0,05–1,8 m en F4) con el LiDAR real y los objetos reales.
- **Odometría:** diverge cuando las ruedas patinan o empujan; no hay localización (sin AMCL/SLAM). Necesaria para navegar en F7+.
- **Mobiliario:** la base de las sillas de 2025 es estimada; las mallas de 2025 sin colisión fiable (porosa/155 k caras).
- **Cadena plano→mundo:** `map2sdf` falla de relleno a ciertas resoluciones; `sdf2map` engorda muros; el piso de prueba era no estanco (entrada sin pasillo) y con una baranda abierta; los muros de IQS pueden traer **columnas, rampas, ventanas, cristales** que el mapa 2D no distingue. Solo se validó con **un** plano externo (un DWG de AutoCAD 2018).
- **Rendimiento:** el LiDAR añade ~300 MB; `/clock` y `/joint_states` a 1 kHz; en el piso de 13 × 11 m el servidor usó ~500 MB: un espacio mucho mayor puede cambiarlo.
- **Licencias:** del plano de IQS (uso/redistribución) y de las mallas AgileX.

## 8. Información que todavía hay que pedir a IQS
1. **El plano oficial** en DXF (preferido) o DWG; si solo hay PDF, vectorial. Versión, fecha y **permiso de uso**.
2. **Unidades, origen/ejes y cotas de control**; si el plano es el «as-built» o el proyecto.
3. **Zona exacta de la competición:** límites, accesos, puertas que cuentan, escaleras/rampas, columnas, desniveles.
4. **Altura de techos/obstáculos** y **huecos reales** (anchos de puertas/pasillos).
5. **Mobiliario y máquinas del día de la prueba:** lista, **dimensiones reales** (modelos CAD o fichas), posiciones previstas, cuáles son fijas.
6. **Checkpoints/elementos de competición** (formato, posición, tamaño) → **F7**, no F6.
7. **TRACER y sensores del equipo actual:** variante confirmada de TRACER, **LiDAR** (modelo, altura, posición, FOV, frecuencia), cámara/IMU si hacen falta.
8. **Reglas de la prueba** que condicionen el escenario (obstáculos, iluminación, suelo, personas).
9. Si pueden facilitar **fotos o medidas** del espacio real para validar el modelo.
**Hasta recibir el plano, F6 no empieza** y no se construye ningún escenario.
