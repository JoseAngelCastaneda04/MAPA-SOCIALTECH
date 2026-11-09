# DETALLE F2 — comandos, medidas y registros

Todas las rutas parten de `F2_PLANO_SIMPLE_GAZEBO/` (la ruta del proyecto contiene un espacio: entrecomillar siempre). Herramientas de F1 usadas **sin modificarlas** (solo lectura): `F1_INVESTIGACION_SOFTWARE/{herramientas,scripts,ws}`. Comprobado al final: ningún archivo de F0 ni de F1 es posterior a `original/`.

## A. Procedencia del archivo

- Página: https://designscad.com/downloads/apartment-unit-floor-plan-with-dimensions-and-wet-areas/ (título de pestaña «Apartment Unit Floor Plan DWG with Dimensions | Designs CAD»). Campos de la web: File Type DWG · Language Portuguese · Units Metric · Materials Concrete, Masonry · Uploaded by Blueprint Hub · Published Jun 3, 2026 · «unit layout for tower B with dimensions and AC prep».
- Descarga (2026-11-07): botón *Free Download* → verificación anti-bot (Cloudflare Turnstile) y temporizador, **hechos por ti**. No se automatizó. Sin login ni pago.
- Términos: https://designscad.com/terms-conditions/ — «Downloaded files may be used for your own personal, educational, or commercial projects. You may not redistribute, resell, or sublicense the files as standalone products.» También prohíben «scrape, mirror, or bulk-download files beyond normal personal use»: se descargó **un** archivo.
- `original/designscad_…_4191.zip` · SHA-256 `82766fb7cf88ea5a039b98a8d52068badf4a84e0790cb29b2a1dbbc563ef7f86` · 4 408 303 B.
- `original/contenido_zip/…_4191.dwg` (extraído del ZIP) · SHA-256 `b22a1c959912ae7e7af2a97585793b2927c32f7510f978402408b4f0533339a1` · 6 497 351 B · `file`: «DWG AutoDesk AutoCAD 2018/2019/2020» (`AC1032`).
- Candidatos descartados antes: 1) *100,54 sqm Unit Type 02* (según su vista previa solo trae el contorno exterior, sin tabiques ni puertas; 🔎 no abierto el DWG), 2) *1BHK Interior Layout* (escala «NS», sin cotas y con el cajetín «shall not be copied, reproduced or used without written consent»), freecads.com (planta de 4 viviendas entrelazadas; descarga con login). Los dos primeros se juzgaron **solo por la ficha y la miniatura**.

## B. Reproducir

```bash
cd "…/MAPA SOCIALTECH/F2_PLANO_SIMPLE_GAZEBO"
H="…/F1_INVESTIGACION_SOFTWARE/herramientas"; PY="$H/venv/bin/python"; SC="…/F1_INVESTIGACION_SOFTWARE/scripts"
# 1 DWG -> DXF (LibreDWG 0.14); 40 MB, 34 026 entidades
"$H/libredwg_gnu/libredwg-0.14/programs/dwg2dxf" -y -o derivados/plano.dxf original/contenido_zip/*.dwg
# 2 aislar el piso (x 3,5..20; y -12..1 m): 10 145 entidades conservadas, 23 881 descartadas
"$PY" -I scripts/recortar_piso.py derivados/plano.dxf derivados/plano_piso_todo.dxf 3.5 20 -12 1
# 3 lazos cerrados de las capas de mampostería (edgeminer, tolerancia 1 mm)
"$PY" -I scripts/cerrar_lazos.py derivados/plano_piso_todo.dxf derivados/plano_piso_muros.dxf \
   "ESTRUTURA - ARQ-STA - ALVENARIA_ESTRUTURAL|ESTRUTURA - ARQ-STA - ALVENARIA_NÃO_ESTRUTURAL"
# 4 DXF -> mapa nav2, 2 cm/celda (el DXF recortado ya declara metros)
"$PY" -I "$SC/dxf_a_mapa.py" derivados/plano_piso_muros.dxf --capas "ESTRUTURA - ARQ-STA - BLOCOS_ESTRUTURAIS" F2_LAZOS_ALVENARIA \
   --res 0.02 --origen bbox --margen 0.2 --out mapa/piso
# 5 mapa -> modelo 3D
source /opt/ros/jazzy/setup.bash; source ../F1_INVESTIGACION_SOFTWARE/ws/install/setup.bash
ros2 run map2sdf map2sdf --map mapa/piso.yaml -o mundo/modelos --format model --wall-height 2.5 --world-name piso_designscad --no-ground
# 6 validar
M="$PWD/mundo/modelos"; export GZ_SIM_RESOURCE_PATH="$M" SDF_PATH="$M"
gz sdf -k mundo/piso_designscad.sdf ; gz sim -s -r -v 4 --iterations 500 mundo/piso_designscad.sdf
"$PY" -I scripts/medir_cotas.py mapa/piso.yaml evidencias/cotas_verificadas.json
# GUI: scripts/lanzar_gazebo_gui.sh "$PWD/mundo/piso_designscad.sdf" "$M"; capturas: scripts/captura_ventana.sh <pid_gz_gui> salida.png
```

Nota: sin `--unidades 6` el paso 4 sobre `derivados/plano.dxf` daría `INSUNITS=4 (x0.001 -> m) … 1x1 px … extensión 0.018 x 0.011 m` (probado). El DXF recortado se crea con `units=6`; esa es la corrección de unidades.

## C. Inspección del archivo (ezdxf 1.4.5 sobre el DXF de LibreDWG)

- Versión `AC1032`, `$INSUNITS=4`, `$MEASUREMENT=1`, `$LUNITS=2`. Extensión −18,0…79,8 × −18,1…11,1 (detalles repartidos). Layouts `F1002` y `Model`.
- Modelspace: 26 510 SOLID, 5 110 LINE, 1 537 LWPOLYLINE, 454 HATCH, 298 CIRCLE, 46 MTEXT, 23 DIMENSION, 17 INSERT, 16 ARC, 15 TEXT. 27 capas con entidades de 41.
- Capas de interés (en la zona del piso): `ESTRUTURA - ARQ-STA - BLOCOS_ESTRUTURAIS` 780 (583 LWPOLYLINE «abiertas»: **576 se cierran geométricamente** —primer vértice = último—, 5 y 9 vértices; 7 no cierran, de 1 cm de grosor; + 197 LINE cortas), `…ALVENARIA_ESTRUTURAL` 119 LINE, `…ALVENARIA_NÃO_ESTRUTURAL` 24 LINE, `…DRYWALL` 264 LINE, `ARQ-STA - PORTAS` 136, `ARQ-STA - JANELAS` 1 219, `…REVESTIMENTOS` 166 LINE, `…GRAUTES` 6 191 (triángulos diminutos de relleno de mortero dentro de los bloques; no se usan).
- Unidades: `INSUNITS=4` pero las 23 `DIMENSION` miden 0,25…1,98 y las MTEXT de `COTAS_ALVENARIA` valen 2,50 / 2,50 / 2,90 / 4,00 / 4,15 / 5,75…; los rótulos 2,50 están separados ≈2,7 m en coordenadas ⇒ **1 unidad = 1 m**. Verificado además midiendo geometría (§E).
- 6 puertas (arcos): centros (12,43; −6,99) (12,07; −6,99) (16,42; −5,66) (11,03; −5,66) (13,64; −6,72) r=0,81 m y (5,09; −3,52) r=0,91 m. Rótulos PM 02 (dormitorios y paso central) y FM 02 (aseos).

## D. Lazos cerrados (`evidencias/logs/cerrar_lazos.log`)

`edgeminer.find_all_loops(Deposit(aristas, gap_tol=1e-3))`:
- `ALVENARIA_NÃO_ESTRUTURAL`: 24 líneas → **5 lazos**: 9,67–11,22 × −6,97…−6,83 (frente del dormitorio 1, 1,55 × 0,14), 9,14–9,28 × −0,77…−0,07 (tabique 0,14 × 0,70), 12,81–13,43 × −0,86…−0,24 y 12,86–13,38 × −0,81…−0,29 (cuadrado de 0,62 y su contorno interior 0,52), 12,13–12,18 (detalle de 5 cm).
- `ALVENARIA_ESTRUTURAL`: 119 líneas → **11 lazos** (los mismos muros de bloques, más tramos de 0,14 × 0,10).
- Se escriben como `LWPOLYLINE` cerradas en la capa `F2_LAZOS_ALVENARIA` (16 en total). **No se une ninguna línea que el CAD no una.** El cuadrado de 0,62 m se rellena entero (el CAD no dice si es pilar o conducto): 🔎 interpretación.

## E. Mapas y medidas

| Mapa | Celda | Tamaño | Ocupadas | Nota |
|---|---|---|---|---|
| `mapa/piso.*` (**maestro**) | 0,02 | 675 × 590, origen (4,7299; −11,32) | 28 634 (11,45 m²) | usado para el modelo 3D |
| `mapa/piso_5cm.*` | 0,05 | 270 × 236 | 4 576 (11,44 m²) | **fallo de `map2sdf`** (§F); medidas idénticas |
| `mapa/referencia_1cm.*` | 0,01 | 1350 × 1179 | — | geometría del CAD a 1 cm, para comparar |
| `mapa/ruta_pdf_derivado/mapa_pdf*.{pgm,yaml}` | 0,02 | 655 × 580, origen (0,0) o alineado (4,93; −11,12) | 26 963 (10,79 m²) | ruta PDF |

Medición (`scripts/medir_cotas.py`: tramo libre continuo a lo largo de una línea por un punto de la habitación; el resultado incluye una celda por conteo inclusivo). Referencia 1 cm da +0,01 en todas las cotas por ese mismo efecto, no por error.

| Cota CAD | Mapa DXF 2 cm | Mapa DXF 5 cm | PDF derivado | Ref. 1 cm (CAD) |
|---|---|---|---|---|
| Dorm. 1 ancho 2,50 | 2,50 (0,000) | 2,50 | 2,52 (+0,02) | 2,51 |
| Dorm. 2 ancho 2,50 | 2,50 (0,000) | 2,50 | 2,50 (0,000) | 2,51 |
| Dorm. 3 ancho 2,90 | 2,90 (0,000) | 2,90 | 2,92 (+0,02) | 2,91 |
| Dorm. 1 fondo 4,00 | 4,00 (0,000) | 4,00 | 4,02 (+0,02) | 4,01 |
| Dorm. 2 fondo 4,00 | 4,00 (0,000) | 4,00 | 4,02 (+0,02) | 4,01 |
| Dorm. 3 lado E 5,75 | 5,76 (+0,010) | 5,75 | 5,76 (+0,01) | 5,76 |
| Puertas WC izq./der., dorm. 1, 2 | 0,90 | 0,90 | 0,90–0,92 | 0,91 → 0,90 |
| Puerta dorm. 3 / entrada | 1,00 / 1,54 | 1,00 / 1,55 | 1,00 / 1,52 | 1,01 / 1,54 |

La «cota» de las puertas es el **radio del arco** (0,81; 0,91 m = ancho de la hoja), **no una cota de hueco**: el plano no acota los huecos. El hueco de obra es 0,90 m en el CAD (rasterizado a 1 cm) y el mapa lo conserva. Las 6 cotas de dormitorios sí son cotas escritas. Puntos y ejes: `evidencias/cotas_verificadas.json`.

Modelo 3D (STL): 1 234 triángulos, 6 regiones de muro, pose = origen del mapa (4,7299; −11,32). Caja local x 0,16…13,30, y 0,20…11,60, z 0…2,50 ⇒ mundo x 4,93…18,03, y −11,12…0,28. CAD (polígonos usados): x 4,930…18,020, y −11,120…0,270 ⇒ error 0,01 m. IoU entre la tapa del STL y el mapa: 0,9955.

## F. Fallo de `map2sdf` (observado, no analizado en su código)

Misma geometría, solo cambia la resolución (`dxf_a_mapa.py --res`); área de la tapa del STL (debería ≈ área de muro):

| m/celda | muro del mapa | tapa del STL |
|---|---|---|
| 0,02 | 11,45 m² | 11,48 ✅ |
| 0,025 | 11,40 | 63,03 ❌ |
| 0,04 | 12,11 | 149,65 ❌ |
| 0,05 | 11,44 | 148,98 ❌ |
| 0,07 | 14,21 | 14,33 (muros engordados por cuantización) |
| 0,10 | 15,07 | 15,28 (idem) |

`extract_regions` es correcto (a 0,05: región mayor 10,9 m², 140 vértices, 0 huecos); el fallo está en la triangulación de la tapa (`mesher._ear_clip`). `--simplify 0,05` lo evita a 0,05 pero deja la tapa en 13,27 m² (≠ 11,44): no se usa. Detectado **midiendo** el STL, porque `gz sdf -k` daba *Valid* y `gz sim` cargaba sin errores con el modelo roto: **esas dos comprobaciones no bastan**.

## G. Gazebo Harmonic (8.15.0)

- `gz sdf -k mundo/piso_designscad.sdf` → `Valid.` · `gz sim -s -r -v 4 --iterations 500` → rc 0, 0 líneas con *error|warn* (`logs/gz_sim_headless.log`).
- Estructura: `mundo/modelos/piso_designscad/{model.sdf, model.config, …_walls.stl}` (estático; colisión y visual con la misma malla) + `mundo/piso_designscad.sdf` (física, plugins, luz, suelo de 26 × 22 m en (11,5; −5,4), `<include>`). Es la estructura de ICAI_A501 (modelo base + `<include>`) y de F1. Coordenadas del mundo = coordenadas del CAD, en metros. El «suelo» es un plano visual/colisión, no una losa del plano.
- Capturas de la ventana de Gazebo de esta sesión (`xwininfo` + `ffmpeg x11grab`, tras comprobar que el PID activo es el mío; nunca `scrot -u`): `01_cenital_norte_arriba.png` (cámara 11,0; −5,4; 15 m, cuaternión (−0,5; 0,5; 0,5; 0,5) como F1), `02_oblicua_suroeste.png`, `03_entrada_oeste.png` (hueco abierto hacia el exterior), `05_puertas_aseos_picado.png` (dormitorios, aseos con sus huecos y salón). La `04` se eliminó por no mostrar nada útil. Una captura inicial incluía parte de otras ventanas del escritorio: **borrada** sin conservar.
- Cualitativo: la perspectiva de la cámara muestra los costados de los muros (la cenital no es ortogonal). Las medidas no salen de las capturas.

## H. Ruta PDF derivado

- `derivados/pdf_derivado/solo_muros.dxf` (solo `BLOCOS_ESTRUTURAIS` + `F2_LAZOS_ALVENARIA`, 796 entidades) → `solo_muros_mm.dxf` (×1000, `INSUNITS=4`, `scripts/dxf_m_a_mm.py`) → `solo_muros_mm.pdf` (A3, 1:50) → `solo_muros_mm.png` (254 ppp, 4 202 × 2 971 px, 0,005 m/px).
- **Es un archivo derivado del DWG, no un PDF independiente ni una prueba de lectura de un PDF de arquitecto.** Es monocromo y vectorial, con el muro dibujado como contorno de bloques.
- `LibreCAD dxf2pdf` con DXF en metros ignora `-p` (salió una hoja de 420 × 297 **m**, y `pdftoppm` falló con «Bogus memory allocation size»): hubo que dar el DXF en milímetros, como en F1. Ejecución: `LD_LIBRARY_PATH=$H/librecad/usr/lib/x86_64-linux-gnu QT_QPA_PLATFORM=offscreen`.
- `raster_a_mapa.py solo_muros_mm.png --m-por-px 0.005 --rellenar --res 0.02`: tinta 13,095 × 11,590 m (el CAD son 13,09 × 11,39; los 0,2 m de más son los 7 fragmentos de 1 cm del borde superior que el mapa DXF no usa). `--cerrar 0/3/5` dio el mismo resultado.
- Comparado con el mapa DXF (alineado por la esquina de la tinta): IoU 0,923; solo-DXF 1 945 celdas (0,78 m²), solo-PDF 274; las discrepancias son franjas de 1 celda en los bordes de muros de 7 celdas. Los 6 huecos de puerta y el cuadrado de 0,62 m coinciden.
- **Condición:** este éxito exige **filtrar antes las capas de muros** y que sean contornos cerrados. Con el piso entero (puertas, cotas, textos, sanitarios) el caso sería el ❌ de F1; **no se probó** en F2.

## I. Qué no se probó

- Un PDF **independiente** del mismo piso, ni PNG/JPG/foto (queda para tu prueba con PNG).
- Un segundo plano real; la repetición del fallo de `map2sdf` en otras geometrías.
- Colisión con el robot, rendimiento, RViz2 (F3) y `sdf2map` sobre este mundo.
- Cotas fuera de los dormitorios; y las miniaturas de los candidatos 1 y 2 no se contrastaron con su DWG.

## J. Cierre de F2 (2026-11-08): comprobación de la versión final y precisión

Autorización del usuario: cierre condicionado a que la versión a 0,02 m/celda supere las comprobaciones geométricas. Se repitieron **sin cambiar ningún archivo existente**:

| Comprobación (0,02 m/celda, `mapa/piso.*`, `mundo/piso_designscad.sdf`) | Resultado |
|---|---|
| Tapa superior del STL (`scripts` ad hoc, suma de áreas de triángulos con z=2,5) | **11,478 m²** frente a 11,454 m² de muro en el mapa → el fallo de relleno **no aparece** ✅ |
| Caja del STL | 13,10 × 11,40 × 2,50 m (CAD 13,09 × 11,39; altura = parámetro) |
| `gz sdf -k` del modelo y del mundo (`SDF_PATH` = `mundo/modelos`) | Valid. ✅ (sin `SDF_PATH` el mundo da «Unable to find uri»: es del entorno, no del modelo) |
| `gz sim -s -r -v 4 --iterations 500` (`logs/gz_sim_headless_cierre.log`) | rc 0, 0 líneas con «error» o «warn» ✅ |
| `medir_cotas.py` sobre `mapa/piso.yaml` | idéntico a §E (≤ 0,01 m en las 6 cotas) ✅ |

### Hallazgo: el mapa de 0,02 m **engorda los muros** (medido, no estimado)

Verdad-terreno geométrica = el mismo DXF rasterizado a 0,0025 m/celda (`dxf_a_mapa.py --res 0.0025`, área de muro **10,534 m²**; a 0,005 da 10,535). Comparación tras llevar todos los mapas a la rejilla de 2,5 mm:

| Mapa | Área de muro | Diferencia | IoU con la verdad | Desviación máx. (sobrante / faltante) | STL: tapa / caja |
|---|---|---|---|---|---|
| 0,02 m (`piso.*`) | 11,454 m² | **+0,920 m² (+8,7 %)** | **0,917** | 0,015 / 0,0125 m | 11,478 m² / 13,10 × 11,40 |
| **0,01 m (`piso_1cm.*`)** | 10,551 m² | +0,017 m² (+0,16 %) | **0,998** | 0,0075 / 0,005 m | 10,558 m² / 13,09 × 11,39 |

Causa (medida, no del código): `dxf_a_mapa.py` marca como ocupada toda celda tocada por un polígono, así que cada borde crece hasta una celda; con ~171 m de contorno de muro, 2 cm engordan el área un 8,7 %. El **STL del modelo de 2 cm hereda ese engorde** (muros ≈ 0,5 cm más gruesos por cara de media).

**Corrección a lo dicho antes:** la tabla de §E atribuía el +0,01 m de la referencia de 1 cm al conteo inclusivo de `medir_cotas.py`. Con la verdad a 0,0025 m el tramo libre sigue siendo **2,51 / 2,91 / 4,01 / 5,76 m**: el **CAD mide +0,01 m más que la cota escrita** (2,50…), no es artefacto. El «0,000» de los dormitorios en el mapa de 2 cm es **cuantización** (el engorde se lleva 1 cm del hueco libre), no mayor fidelidad. Errores contra la **geometría del CAD** (no contra la cota nominal): mapa 2 cm → −0,01 m en las 5 cotas de dormitorio medidas (2,50 / 2,50 / 2,90 / 4,00 / 4,00 frente a 2,51 / 2,51 / 2,91 / 4,01 / 4,01) y 0,00 en el lado E (5,76); mapa 1 cm → 0,00 en las seis (`logs/cotas_medidas_1cm.txt`).

### Versión de alta precisión añadida (0,01 m/celda) — no sustituye a la de 0,02

`mapa/piso_1cm.{pgm,yaml}` (1350 × 1179, origen idéntico (4,7299; −11,32)); `mundo/modelos/piso_designscad_1cm/` (1 540 triángulos, 91 regiones de muro) y `mundo/piso_designscad_1cm.sdf` (mismo mundo, otro `<include>`). Mismos comandos de §B con `--res 0.01` y `--world-name piso_designscad_1cm`. Comprobaciones: tapa 10,558 m² vs 10,551 m² ocupados (**sin relleno**), `gz sdf -k` Valid, 500 iteraciones sin errores (`logs/gz_sim_headless_1cm.log`), captura de la ventana de Gazebo `capturas_gazebo/06_cenital_1cm.png`. Huecos de puerta 0,91 / 1,01 / 1,54 m (verdad 0,0025: 0,91 / 1,01 / 1,54). Mismo límite: **resolución sin relación demostrada con el fallo**: que 0,01 funcione no explica por qué fallan 0,025–0,05 (ver §F; causa sin analizar). Los modelos conservan 0,02 como solicitado y 0,01 como opción para máxima fidelidad; elegir cuál usa F3 queda pendiente (ver `RESUMEN F2.md` §8).

### Herramientas y versiones

LibreDWG 0.14 (`dwg2dxf`, compilada en F1) · ezdxf 1.4.5 (`importer`, `edgeminer`) · OpenCV 5.0.0 · NumPy 2.5.4 · Python 3.12.3 · LibreCAD (CLI `dxf2pdf`, F1) · poppler `pdftoppm` 24.02.0 · `map2sdf`/`sdf2map` (workspace F1, sin modificar) · Gazebo Sim 8.15.0 (Harmonic), gz-sdformat 14.9.0 · ROS 2 Jazzy.

### Baranda y zona técnica (decisión del usuario, 2026-11-08)

No se añade muro ni se inventan dimensiones. La baranda de la zona técnica (≈ 2,2 m) **no está reconstruida**: el CAD solo trae una línea sin grosor. **Zona a revisar al integrar el Tracer (F5)**: el robot podría salir del piso por ahí, y el mapa de ocupación la trata como libre.

### Huellas de los archivos finales (SHA-256, primeros 16 caracteres)

`mapa/piso.pgm` 8a2e68660f82305d · `mapa/piso_1cm.pgm` e0b52cb2708d8d9f · `piso_designscad_walls.stl` ba97f55b765661dd · `piso_designscad_1cm_walls.stl` 913942a88a24eb5b.

### Qué se conserva

Nada anterior se eliminó. Capturas 01, 02, 03, 05 (0,02) y 06 (0,01); mapas 5 cm y referencia 1 cm; registros previos. Archivos nuevos: `logs/gz_sim_headless_cierre.log`, `dxf_a_mapa_1cm.log`, `map2sdf_1cm.log`, `gz_sdf_check_1cm.log`, `stl_area_1cm.log`, `cotas_medidas_1cm.{txt,json}`, `gz_sim_headless_1cm.log`, `gz_gui_1cm.log`.
