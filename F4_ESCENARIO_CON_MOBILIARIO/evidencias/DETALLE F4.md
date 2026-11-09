# DETALLE F4 — Escenario con mobiliario (anexo de `RESUMEN F4.md`)
**Estado: F4 — CERRADA Y VALIDADA PARA EL ESCENARIO PROBADO, CON LIMITACIONES DOCUMENTADAS** (cierre autorizado el 2026-11-08; ver §M).
Rutas relativas a `F4_ESCENARIO_CON_MOBILIARIO/` salvo indicación. Fecha de trabajo: 2026-11-08. Entorno: Ubuntu 24.04, ROS 2 Jazzy, Gazebo Sim 8 (Harmonic), RViz2, Python 3.12 (numpy, OpenCV, PyYAML, matplotlib del sistema; sin instalar nada).

## A. Revisión previa (F0–F3) — archivos reales
| Qué | Ruta real |
|---|---|
| Mundo definitivo F2 (1 cm) | `F2_PLANO_SIMPLE_GAZEBO/mundo/piso_designscad_1cm.sdf` (incluye `model://piso_designscad_1cm`, suelo plano 26×22 m y luz) |
| Modelo 3D del piso | `F2/mundo/modelos/piso_designscad_1cm/{model.sdf,*_walls.stl}`; pose (4,7299; −11,32; 0) |
| Mapa 0,01 m/celda | `F3_MAPA_RVIZ2/mapa/piso_1cm.{pgm,yaml}` (1350×1179, origen (4,7299; −11,32), valores 0/254, `occupied_thresh` 0,65) |
| Config RViz2 | `F3/config/piso_1cm.rviz`; launch `F3/launch/mapa_rviz.launch.py` |
| Demo | `F3/scripts/{demo,demo_gazebo,parar_demo}.sh` (el nombre «prueba1.sh» también existe; no se usó) |
| Modelos 2025 | `F0_AUDITORIA_REPOSITORIOS/SocialTech-Gazebo/models/{table1,table2,chair,door,checkpoint,…}` (33 modelos) |
| Herramientas | `F1/ws/install` → `map2sdf`, `sdf2map` (`source F1/ws/install/setup.bash`) |
Las rutas coinciden con las de `ARCHIVOS PARA F4.md`. Confirmé que ningún archivo de F0–F3 es más reciente que el inicio de F4 (`find -newer`).

## B. Modelos originales de SocialTech 2025
Medidos con `scripts/medir_malla.py` (solo numpy). El OBJ de SketchUp es **Y‑arriba**.
| Modelo | `model.sdf` original | Malla | Tris | Bbox (marco OBJ) | Material | Colisión original |
|---|---|---|---|---|---|---|
| table1 | `<model><pose>… 1.5708 0 0` + `visual/collision <pose> 1.5708 0 0` | `meshes/mesa1.obj` (768 kB) | 10 054 | x 0–1,736; y 0–0,796; z −0,774–0 | `.mtl` + `Metal_Corrugated_Shiny.jpg` | la misma malla |
| table2 | idem | `mesa2.obj` (233 kB) | 4 554 | x 0–0,502; y 0–0,7395; z −1,948–0 | `Steel_Brushed_Stainless.jpg` | la misma malla |
| chair | sin `<model><pose>`; visual/collision 1,5708 | `silla.obj` (16 MB; `Chair.obj` de 270 tris existe pero no lo referencia el SDF) | 155 001 (79 386 vértices) | x ±0,2403; y 0–0,8378; z −0,2648–0,2579 | `silla.mtl`, 3 JPG; Kd = 0 en `brsw` (negro) | la misma malla |
| door | 1,570796 | `door.obj` | 1 808 | x −0,84–0; y 0–2,02; z −0,044–0,091 | `.mtl` + jpg | la misma malla |
| checkpoint | sin malla | cilindro r = 0,125 m, largo 0,0001 m, color (0,004; 0,129; 0,412) | — | — | — | **sin colisión** |

**Orientación y origen (investigación pedida):**
1. `gz sdf -p` sobre un `<include>` con pose muestra que el `<model><pose>` del archivo **se sustituye** por la pose del include; queda solo el giro del `<visual>`/`<collision>` (Rx 90°): Y‑arriba → Z‑arriba. Con ello mesa1 mide 1,736 (X) × 0,774 (Y) × 0,796 (Z) y es un trapecio (lado ancho hacia −Y a yaw 0 en la figura de RViz).
2. **Origen:** mesa1 y mesa2 tienen la **esquina mínima** de la huella en (0,0) → al colocarlas «en (x, y)» el cuerpo queda desplazado (+0,868/+0,387 m y +0,251/+0,974 m respecto de su centro). La silla está centrada (desplazamiento −0,0035 m en Y). Esto explica los objetos «desplazados» vistos en F2.
3. **Frente de la silla:** por franjas de altura, el respaldo (z > 0,5) está en y +0,17…+0,26 → mira a **−Y** a yaw 0. Convención del YAML: silla N (yaw 0) mira al sur, S (180°) al norte, W (90°) al este, E (−90°) al oeste.
4. **Estructura de la silla (para la colisión):** 62 450 de 79 386 vértices están a z < 0,009 (huella plana, r_max 0,35); asiento z 0,35–0,43 (x ±0,223; y −0,258…0,181); respaldo z 0,50–0,84 (x ±0,194; y 0,168…0,265); entre 0,05 y 0,35 no hay vértices (triángulos largos sueltos). La **altura de la base/columna no está en los datos**: la base de 4 cm de la colisión simple es una **estimación**.
5. Funcionamiento en Harmonic: los 5 modelos validan (`gz sdf -k`); el mundo amueblado carga con 0 errores. `door` no se usó (origen en la bisagra, sin hoja en F2: «puertas = huecos abiertos»); `checkpoint` no se usa en F4.

## C. Modelos de F4 (`scripts/crear_modelos.py`)
Genera `modelos/` copiando mallas/materiales de los originales y escribiendo `model.sdf` nuevo con `visual`/`collision` `<pose>` = (−cx, −cy, −zmin, 1,570796, 0, 0). Dimensiones medidas en `modelos/dimensiones.json`.
| Modelo F4 | Desplazamiento aplicado (x, y, z) | Dimensiones X×Y×Z (yaw 0) | Colisión |
|---|---|---|---|
| mesa1 | (−0,868; −0,387; 0) | 1,736 × 0,774 × 0,7962 | malla original |
| mesa2 | (−0,251; −0,974; 0) | 0,502 × 1,948 × 0,7395 | malla original |
| silla | (0; −0,00345; 0,00001) | 0,4806 × 0,5227 × 0,8378 | 3 cajas/cilindros: base estimada (cil. r 0,25, h 0,04), asiento (0,446×0,439×0,08 en (0; −0,0385; 0,39)), respaldo (0,388×0,097×0,41 en (0; 0,2165; 0,635)) |
| silla_malla | igual | igual | malla de 155 k (solo pruebas, `--malla`) |
| caja / papelera | — | 0,40×0,40×0,50 / ⌀0,40×0,60 | primitiva = visual |
Los modelos de caja y papelera son **inventados por F4** como obstáculos de prueba (colores naranja/verde).

## D. Procedimiento de generación (editable)
`config/mobiliario.yaml` (única fuente de verdad: id, modelo, x, y, z, yaw_deg + `mapa_base`, `slice_z`) → `scripts/regenerar.sh`:
1. `generar_mundo.py` → `mundo/piso_amueblado.sdf` (piso de F2 por `model://` + `<include>` por objeto; comentario «GENERADO») y `mundo/solo_mobiliario.sdf`.
2. `gz sdf -k` de ambos.
3. `sdf2map --input solo_mobiliario.sdf --density 40000 --occupancy-grid … --slice-z-min/max` (0,01 m; 0,5 s; 126–138 MB) → `mapa/capa_mobiliario.{pcd,yaml,pgm}`.
4. `combinar_mapas.py --nube capa.pcd --z 0,05 1,8` → `mapa/piso_amueblado.{pgm,yaml}` + `capa_alineada.pgm`.
Densidad: 400 puntos/m² deja huecos a 1 cm (celdas vacías en caras verticales); 40 000 los cubre y el cierre de 1 celda rellena el resto. `scripts/mobiliario.py` añade/mueve/quita líneas del YAML (texto; conserva comentarios).

**Por qué la unión desde la nube y no el mapa de `sdf2map`:** el origen de la rejilla de `sdf2map` = mínimo de la nube − 1 celda; al mover un objeto cambia, y el remuestreo por coordenadas desplaza ±1 celda a **otros** objetos. La prueba de §H lo detectó (40 celdas fuera de las huellas). La nube se rasteriza con el mismo criterio que `sdf2map` (`floor((p − origen)/res)`, banda z, cierre 3×3 radio 1) pero **en la rejilla de la base**: cada objeto cae siempre en las mismas celdas. Control: nube vs rejilla de `sdf2map` remuestreada → IoU 0,9979 (4 celdas solo en la nube, 66 solo en la rejilla). **No se hace resta** ni se toca el muro: `ocupado = base OR capa`; el script comprueba `assert (nuevo | ~base).all()`.
Se probó también el camino de F1 (sdf2map sobre el mundo completo): engorda muros; no se usó.

## E. Comprobación del mapa (`scripts/comprobar_mapa.py`, `evidencias/logs/comprobacion_final.json`)
- **A:** tamaño, resolución, origen idénticos; celdas de pared de F3 liberadas = 0 (de 105 509); celdas nuevas 33 212 = capa alineada (0 diferencias).
- **B:** huecos (m) antes → después de las 6 puertas de `F2/evidencias/cotas_verificadas.json`: 0,91/0,91/0,91/0,91/1,01/1,54 → idénticos.
- **C:** distancia mínima mueble–pared (distance transform): mesa_1 1,01 · mesa_2 0,23 · silla_N 1,66 · silla_S 0,92 · silla_W 0,48 · silla_E 0,46 · caja 0,33 · papelera 0,18 m; ningún solape.
- **D:** huella esperada dibujada **sin sdf2map**: triángulos del OBJ proyectados (mesas) o primitivas (silla, caja, papelera) con la pose del YAML. IoU frente a la capa: mesa_1 0,975 · mesa_2 0,976 · silla_N 0,941 · silla_S 0,978 · silla_W 0,941 · silla_E 0,962 · caja 0,952 · papelera 0,958; error máximo de bbox 0,01 m. (IoU < 1 por el cierre morfológico y el muestreo, ≤ 1 celda.)

## F. Gazebo ↔ RViz2 (`scripts/comparar_gazebo_rviz.py`, `logs/comparacion_gazebo_rviz.json`)
Con la demo en marcha: poses de `/world/piso_amueblado/pose/info` frente al YAML → error 0,0000 m / 0,000° en los 8 objetos. `/map` (QoS transient local) frente al PGM → 0 celdas distintas, 138 721 ocupadas, 0 paredes de F3 liberadas, frame `map`. Huellas del `/map` frente a las esperadas con la pose de Gazebo: error de bbox 0,01 m en los 8; centro ≤ 0,01 m.
**Píxeles de RViz2** (`scripts/rviz_aislado.sh` + `medir_rviz_mobiliario.py`; config `piso_amueblado_zoom.rviz`, 170 px/m, centro (8,9; −5,3), display Xephyr :5, viewport 1120×908): error de bbox mesa_1 0,012 · mesa_2 0,006 · silla_N 0,008 · silla_S 0,003 · silla_W 0,008 · silla_E 0,012 · caja 0,010 · papelera 0,009 m (≤ 2 px). Una primera medida dio 0,026 m en mesa_1 por contaminarse con el borde de la silla vecina (ventana de ±4 px); se corrigió a ±1 px y se repitió.
Limitación heredada de F3: la comparación es del SDF cargado y de la pose en ejecución; las capturas de Gazebo son cualitativas.

## G. Colisiones (`scripts/prueba_colisiones.py`; `logs/prueba_colisiones{,_malla}.json`)
Bolas dinámicas r = 0,05 m, m = 0,2 kg, fricción 0, soltadas desde z = 1,2 m; se espera `z = h + 0,05` tras 6 s de **tiempo de simulación**.
| Bola | Esperado | Silla simple | Silla malla |
|---|---|---|---|
| tablero mesa_1 | 0,846 | 0,846 ✅ | 0,846 ✅ |
| tablero mesa_2 | 0,790 | 0,780 (−9,5 mm, sin explicar; el centro de la mesa tiene una ranura visible) | igual |
| caja | 0,55 | 0,55 ✅ | ✅ |
| papelera | 0,65 | 0,65 ✅ | ✅ |
| asiento silla_N | — | 0,480 (cara superior 0,43) | **0,466** (superficie real de la malla 0,416) |
| suelo | 0,05 | 0,05 ✅ | ✅ |
| lanzada −2 m/s contra la caja (x₀ = 10,9) | 10,45 | 10,45 ✅ | 10,45 ✅ |
| lanzada −2 m/s contra la pared sur | no atraviesa | y = −6,78 ✅ | ✅ |
Lecciones: (1) `VelocityControl` en las bolas de caída las congelaba (impone la velocidad cada paso); solo lo llevan las laterales. (2) Con fricción por defecto la bola lateral se detenía a 14 cm: fricción 0. (3) Una bola lateral a z = 0,05 contra silla_E **atravesó** la silla con la malla original (7,07) y **pasó por encima** de la base simple de 4 cm → no hay prueba lateral válida de la base de la silla; se sustituyó por la caja. (4) La colisión simple eleva el asiento 1,4 cm frente a la malla.

## H. Prueba de automatización (`scripts/prueba_mover_silla.py`; `logs/prueba_mover_silla.json`)
Silla_W (7,75; −4,90; 90°) → (9,90; −3,30; 135°). Zona libre: sin solape con paredes ni objetos, 0,834 m de pared. Gazebo (servidor headless con el mundo regenerado, `pose/info`): (9,9; −3,3; 135,0°). Mapa: huella nueva ocupada 98,6 % (0 % en el mapa anterior); núcleo de la huella antigua 1 961 celdas, ocupadas antes 1 961 / **después 0**; celdas cambiadas 4 814, **0** fuera de las dos huellas (±4 cm), **0** sobre pared; 6 puertas iguales; `APROBADO: true`; YAML restaurado e idéntico (`diff`). Figura: `figuras/mapas_base_actualizado_movimiento.png`.
Primera ejecución: `APROBADO: false` por 40 celdas fuera de las huellas (remuestreo de la rejilla, §D); no se relajó el criterio: se cambió el método.
Añadir/quitar: `mobiliario.py anadir silla_X silla 10.0 -3.3 45` → regenerar → IoU 0,970, 0 paredes liberadas; luego `mover` + `quitar` → `piso_amueblado.pgm` y `piso_amueblado.sdf` con **MD5 idéntico** al inicial (`piso_amueblado.pgm` d5ad…; `piso_amueblado.sdf` 3f46…).

## I. Rendimiento
- Headless (`gz sim -s -r --iterations 500`, 3 repeticiones, `logs/carga_headless.txt`): F2 2,63–2,66 s / 147 MB; F4 silla simple 2,67–2,68 s / 174–175 MB; F4 silla malla 3,41–3,45 s / 405–406 MB. 0 errores/avisos.
- GUI 30 s (`scripts/medir_rendimiento.sh`): F2 servidor 128 MB, 22,7 % CPU; GUI 391 MB, 121 %. F4 servidor 156 MB, 24,8 %; GUI 524 MB, 137 %. Tiempo real 0,999 en ambos. (La GUI usa más CPU porque renderiza; no medí qué parte corresponde a las texturas de la silla.)
- Avisos GUI: 2 × `libEGL warning: egl: failed to create dri2 screen` y 3 × `pci id … driver (null)` (del driver gráfico; no comprobé si aparecen también sin mobiliario). RViz2: solo el error GLSL de F3.
- `sdf2map` de la capa: 0,45 s (silla simple), 0,6 s (malla); capa 307×279 celdas; nube 525 680 puntos (6,3 MB).
- Arranque de la demo: `map_server` activo a ~1,9 s; `piso_amueblado/stats` publicado a ~4,0 s (3 arranques).

## J. Demostración y cierre
`scripts/demo.sh [mundo] [config_rviz]` lanza `demo_gazebo.sh` (cámara cenital) y `launch/mapa_rviz.launch.py` (copia de F3 apuntando al mapa y config de F4, con argumento `config:=`). `scripts/parar_demo.sh` envía SIGINT/SIGTERM al **grupo de procesos** guardado en `/tmp/f4_demo/*.pid`; no usa `pkill`. 3 ciclos: 0 procesos residuales. Procesos lanzados a mano para mediciones (gz sim base F2, Xephyr, rviz2 aislado, gz sim de pruebas) se cerraron por PID o grupo propio.

## K. Incidencias y cambios de método
1. **Capturas que incluían el escritorio:** (a) la captura de Gazebo recogió un aviso de escritorio («Diseño de formatos…») → borrada; recorte de los 62 px superiores (`captura_*_recorte.sh`). (b) Una captura de RViz por `ffmpeg x11grab` recogió una ventana **de tu navegador** (la ventana de RViz no estaba al frente aunque el script comprobó el foco antes) → **borrada al instante**; lo vi al abrir el archivo. Desde entonces las medidas de RViz usan Xephyr (display aislado) y no se captura tu pantalla. Las capturas conservadas se revisaron una a una.
2. `gz service /gui/screenshot` responde «true» pero no escribe el archivo (ni con ruta sin espacios); no investigado.
3. Un `gz sim` de la línea base F2 quedó vivo (el `setsid` devolvió otro PID); lo cerré por su PID (116843) tras listarlo, sin tocar otros.
4. Mis supuestos corregidos en el camino: la columna de la silla (invención mía) se eliminó de la colisión; el asiento estaba 5 cm alto (se midió de la malla).

## L. Archivos
`config/` (`mobiliario.yaml`, `piso_amueblado.rviz`, `…_zoom.rviz`) · `modelos/` · `mundo/` (`piso_amueblado.sdf`, `…_malla.sdf`, `solo_mobiliario*.sdf`) · `mapa/` (`piso_amueblado.{pgm,yaml}` = **mapa actualizado**; `capa_*`) · `launch/` · `scripts/` (21) · `evidencias/{capturas_gazebo,capturas_rviz,figuras,logs}`.

## M. Cierre (2026-11-08)
Cierre autorizado por el responsable; resultados aprobados sin repetir pruebas (ver `RESUMEN F4.md` §11). Limitaciones documentadas: (1) colisión lateral de la silla no completamente validada (§G lección 3); (2) base de ruedas estimada (§B.4, §C); (3) 9,5 mm de diferencia en mesa_2 (§G); (4) banda z 0,05–1,8 m pendiente del lidar del Tracer; (5) render de Gazebo solo cualitativo (§F). Archivos y evidencias conservados; F0–F3 sin modificar. Siguiente: `evidencias/ARCHIVOS PARA F5.md`; F5 no iniciada.
