# DETALLE F1 — comandos, medidas y evidencias

Equipo: Ubuntu 24.04.5 nativo, ROS 2 Jazzy, Gazebo Sim 8.15.0 (Harmonic), Python 3.12.3.
Todo se ejecutó en `F1_INVESTIGACION_SOFTWARE/` sin `sudo` y sin instalar nada en el sistema.

## 1. Repositorios (en `repos/`, sin modificar)

| Repo | URL | Rama | Commit | Fecha |
|---|---|---|---|---|
| map2sdf | https://github.com/atinfinity/map2sdf | main | `fde43ff` | 2026-07-11 |
| sdf2map | https://github.com/atinfinity/sdf2map | main | `66feb61` | 2026-07-10 |
| linorobot2 | https://github.com/linorobot/linorobot2 | jazzy | `f6b0bd0` | 2026-09-29 |
| scenery_builder | https://github.com/secorolab/scenery_builder | devel | `b0e7abe` | 2026-09-24 |
| rmf_traffic_editor | https://github.com/open-rmf/rmf_traffic_editor | main | `9cb2a6b` | 2026-11-03 |
| image2gazebo | https://github.com/salihmarangoz/image2gazebo | master | `8f53ec2` | 2022-04-20 |

Clonados con `--depth 50`. Licencias: LICENSE de cada repo (Apache-2.0 salvo image2gazebo, MIT). En la raíz de `scenery_builder` no hay LICENSE (la búsqueda de GitHub tampoco devuelve licencia).

## 2. Plano de prueba

`pruebas/plano_test/crear_plano_test.py` genera `plano_test.png` y `.yaml`: 10 × 8 m, 0,05 m/px (200 × 160 px), origen (0, 0, 0), muros exteriores y dos interiores, 3 huecos de puerta de ≈ 0,9 m. Es sintético: no sustituye al plano real de IQS.
Aviso: por redondeo (`int(0.15/0.05)` = 2) los muros miden 2 px = 0,10 m, no 0,15 m.

## 3. Reproducción

```bash
cd F1_INVESTIGACION_SOFTWARE && source /opt/ros/jazzy/setup.bash
mkdir -p ws/src
ln -sfn ../../repos/map2sdf ws/src/map2sdf
ln -sfn ../../repos/sdf2map ws/src/sdf2map
ln -sfn ../../repos/linorobot2/linorobot2_gazebo ws/src/linorobot2_gazebo
cd ws && colcon build --symlink-install && source install/setup.bash && cd ..
# sdf2map necesita libpcl-dev (ya instalado en este equipo)

# A) mundo completo
ros2 run map2sdf map2sdf --map pruebas/plano_test/plano_test.yaml -o pruebas/map2sdf/world --wall-height 2.5 --world-name vivienda_test
gz sdf -k pruebas/map2sdf/world/vivienda_test.sdf        # → Valid.
gz sim -s -r --iterations 500 pruebas/map2sdf/world/vivienda_test.sdf

# B) modelo de muros + muebles de 2025
ros2 run map2sdf map2sdf --map pruebas/plano_test/plano_test.yaml -o pruebas/integrado/modelos --format model --wall-height 2.5 --world-name vivienda_walls --no-ground
M="$PWD/pruebas/integrado/modelos:$PWD/../F0_AUDITORIA_REPOSITORIOS/SocialTech-Gazebo/models"
export GZ_SIM_RESOURCE_PATH="$M" SDF_PATH="$M"
gz sdf -k pruebas/integrado/mundo_integrado.sdf
gz sim -s -r -v 4 --iterations 300 pruebas/integrado/mundo_integrado.sdf

# C) mapa con mobiliario
ros2 run sdf2map sdf2map --input pruebas/integrado/mundo_integrado.sdf --output pruebas/integrado/mapa.pcd \
  --voxel 0.05 --exclude-ground --no-download --model-path "$M" \
  --occupancy-grid pruebas/integrado/mapa.yaml --grid-bounds slice --grid-margin 0.0
```

Nota: `gz sdf -k` resuelve `model://` con `SDF_PATH`, no con `GZ_SIM_RESOURCE_PATH`.

## 4. Resultados

**map2sdf** (`pruebas/map2sdf/`): `160x200 cells -> 2 wall regions, 142 triangles`. STL: mín (0, 0, 0), máx (10, 8, 2,5) m, medido leyendo los triángulos del STL binario. El SDF referencia el STL con ruta relativa. No he averiguado por qué cuenta 2 regiones.
`log_gzsim_headless.txt` queda vacío: ningún error ni aviso.

**sdf2map, solo muros** (`pruebas/sdf2map/`): 96 710 puntos muestreados, 60 607 tras voxel; rejilla 203×163, 3040 celdas ocupadas (original: 2706).
Comparación con el plano original (transformada de distancia, mejor alineación a fila 2, columna 2):
- original → regenerado: media 0,62 px, máx 1,9 px
- regenerado → original: media 0,34 px, máx 1,9 px
- IoU 0,43 (baja por tratarse de muros de 2 px; no indica un desplazamiento grande).
Con `--grid-close 0`: 1824 celdas, muros huecos (solo 1–2 puntos por columna). Con cierre 1 el muro pasa de 2 a 4 px.

**Mundo integrado** (`pruebas/integrado/`): `gz sdf -k` → `Valid.`; `gz sim` sin errores. Con `sdf2map --verbose`:
`muros` en (0,0,0), `mesa1` en (7,5; 6; 0; yaw 1,5708), `silla1` en (7,5; 5,2; 0; 0). Rejilla 203×163, 3582 celdas ocupadas (+542 respecto al mapa sin muebles). Zona del mobiliario en el mapa: x ∈ [6,73; 7,73], y ∈ [4,93; 7,18] (sonda restringida a la zona).
Huecos de puerta: los 3 puntos de hueco están libres en original y regenerado. Una sonda sobre un muro interior dio "libre" en el regenerado (desfase ≤ 1 celda); no la he vuelto a medir.
Imagen: `comparacion_plano_vs_mapa.png`.

## 5. Fallos y bloqueos

- `colcon build` de `sdf2map`: avisos de PCL/Eigen (`-Wmaybe-uninitialized`, CMP0144, pcap deshabilitado), pero compila.
- `image2gazebo/create_world.sh` ejecuta `sudo apt install png23d imagemagick bc` si faltan: **no ejecutado**.
- `scenery_builder`: `pyproject.toml` exige Python ≥ 3.11, `bpy==4.4.0` y dependencias git fijadas a forks (`rdflib`, `FloorPlan-DSL`, `ifcld`, `robofair`): **no instalado**.
- `rmf_traffic_editor`: el README menciona `ignition` para generar mundos; no hay mención de `gz sim`/Harmonic: **no probado**. No hay paquetes `rmf_*` instalados en el sistema.
- `linorobot2 world_creator`: compila pero es una GUI de tkinter: **no ejecutado**.

## 6. Datos aún sin comprobar

Vista en la interfaz de Gazebo; colisión con el robot; rendimiento con las 12 sillas; comportamiento con un plano real (muros más finos, puertas, ruido); compatibilidad con `origin` con rotación (yaw ≠ 0); entradas DXF/PDF/DWG (ninguno de los candidatos probados las admite directamente). → Las entradas DXF/PDF se resuelven en la ampliación siguiente; DWG sigue pendiente.

---

# AMPLIACIÓN F1 — Conversión de DXF, DWG y PDF (detalle)

## A. Entorno y herramientas (todo dentro de `F1_INVESTIGACION_SOFTWARE/`, sin `sudo`)

| Herramienta | Versión / origen | Cómo se obtuvo |
|---|---|---|
| ezdxf | 1.4.5 (MIT) | `python3 -m venv herramientas/venv && herramientas/venv/bin/pip install ezdxf matplotlib numpy opencv-python-headless pyyaml` |
| LibreCAD | 2.2.0.2-1build3 (repos Ubuntu, GPL-2) | `apt-get download librecad librecad-data libmuparser2v5` y `dpkg -x` en `herramientas/librecad/` (no instalado en el sistema); se ejecuta con `LD_LIBRARY_PATH` y `QT_QPA_PLATFORM=offscreen` |
| poppler-utils | 24.02.0 (ya instalado) | `pdftoppm`, `pdfimages`, `pdfinfo` |
| LibreDWG | 0.13.4.8043 (GPL-3) | `gh release download`; SHA-256 `149d61ec…2137e5` = el de `dist.sha256`. **No compilado** |

`libredwg-tools` y FreeCAD **no** están en los repositorios de Ubuntu 24.04 (`apt-cache`). ODA File Converter (propietaria) no se instaló.

## B. Plano de referencia

`pruebas/vivienda_3formatos/generar_vivienda.py` → `vivienda.dxf` (R2010), `verdad_terreno.json`, `verdad_terreno_muros_1cm.npy`.
Unidades mm (`$INSUNITS=4`), origen CAD en la esquina SO exterior, Y hacia arriba. Capas: `A-MUROS` (9 `LWPOLYLINE` cerradas), `A-PUERTAS` (3 líneas + 3 arcos), `A-COTAS` (2 `DIMENSION`), `A-TEXTO`, `A-MOBILIARIO` (2 `INSERT`), `A-EJES`.
Verdad-terreno: área de muros 7,915 m². Muros: ext 0,20 m, int 0,10 m. Huecos: P1 sur x 4,55–5,45; P2 interior N-S y 2,0–2,9; P3 interior E-O x 2,0–2,9.

## C. Scripts propios (justificación)

| Script | Líneas | Por qué hace falta |
|---|---|---|
| `scripts/dxf_a_mapa.py` | ~70 | Ninguna herramienta existente da "capas de un DXF → mapa nav2 con la escala del CAD". Usa ezdxf. No detecta puertas, no cierra líneas, no limpia. |
| `scripts/raster_a_mapa.py` | ~100 | `pdftoppm` solo da imagen. Hace máscara de tinta, calibración, relleno, apertura, enderezado, remuestreo y escribe PGM+YAML. |
| `scripts/medir_mapa.py`, `resumen_medida.py` | ~90 | Evaluador común: mide en metros contra la verdad-terreno. |
| `scripts/lanzar_gazebo_gui.sh` | 8 | Abre un mundo en la GUI con las rutas de modelos. |

## D. Prueba A — DXF

```bash
# A1 ezdxf
herramientas/venv/bin/python scripts/dxf_a_mapa.py pruebas/vivienda_3formatos/vivienda.dxf --capas A-MUROS --res 0.05 --out pruebas/A_dxf/ezdxf/mapa_0.05
herramientas/venv/bin/python scripts/medir_mapa.py pruebas/A_dxf/ezdxf/mapa_0.05.yaml
# A2 LibreCAD (gráfica)
export LD_LIBRARY_PATH="$PWD/herramientas/librecad/usr/lib/x86_64-linux-gnu" QT_QPA_PLATFORM=offscreen
herramientas/librecad/usr/bin/librecad dxf2pdf -s 0.01 -p 420x297 -c -t pruebas/A_dxf/librecad pruebas/A_dxf/librecad/solo_muros.dxf
pdftoppm -r 254 -png solo_muros.pdf solo_muros          # 254 dpi y 1:100 => 1 px = 1 cm
herramientas/venv/bin/python scripts/raster_a_mapa.py solo_muros-1.png --m-por-px 0.01 --cerrar 3 --rellenar --quitar-texto 20 --res 0.05 --out mapa
# Cadena completa
ros2 run map2sdf map2sdf --map pruebas/A_dxf/ezdxf/mapa_0.05.yaml -o pruebas/A_dxf/gazebo/modelos --format model --wall-height 2.5 --world-name vivienda_dxf --no-ground
gz sdf -k pruebas/A_dxf/gazebo/mundo_dxf.sdf
ros2 run sdf2map sdf2map --input pruebas/A_dxf/gazebo/mundo_dxf.sdf --output mapa.pcd --voxel 0.05 --exclude-ground --no-download --model-path "$M" --exclude '^(mesa1|silla1)$' --occupancy-grid mapa_regenerado.yaml --grid-bounds slice --grid-margin 0
```

Las 8 comprobaciones pedidas:

| Comprobación | Resultado |
|---|---|
| 1. Unidades | ezdxf lee `$INSUNITS=4` (mm) → factor 0,001. Si falta, el script **aborta** salvo `--unidades`. LibreCAD: no las lee; se asume la escala de impresión (`-s 0.01`) y se verifica que el recuadro mida 10,010 × 8,010 m (1 px de línea de más). |
| 2. Escala | ezdxf: exacta. LibreCAD: correcta al respetar `-s`; el PDF es A3 1191×842 pt. |
| 3. Muros vs anotaciones | ezdxf: por **capa**. LibreCAD: solo por **color** de capa (lo que imprime). Eso falla si una capa se superpone (hoja de puerta sobre el canto del muro). |
| 4. Aberturas | Se conservan como huecos entre polilíneas (3/3 en A1 y A2 filtrado). No se identifican como puertas. |
| 5. Resolución | 0,05 y 0,025 m: error 0 (cotas múltiplo de celda). 0,07 y 0,10 m (margen 0,03 m): error máx. 0,08 y 0,10 m. |
| 6. Coordenadas | ezdxf: origen CAD (0,0) o mínimo de la capa (`--origen`). LibreCAD/PDF: **se pierde**; el origen es la esquina de la tinta. |
| 7. Eje Y | CAD Y arriba → fila 0 del PGM = Y máx. Verificado con el plano asimétrico en Gazebo (cenital con norte arriba coincide). |
| 8. Correspondencia con el CAD | IoU 1,000 (A1 a 0,05). Distancias en metros en la tabla E. |

Fallo hallado y explicado (A2, todas las capas): `solo 2 de 9 muros se rellenan`. Causa: la hoja de P1 se dibuja en x = 4,55 m **sobre** el canto del muro (negro→verde), lo que abre un hueco de 10 px en su contorno y el relleno se escapa. Hipótesis confirmada filtrando la capa con ezdxf (`solo_muros.dxf`): error máx. 0,05 m. El `--cerrar 3/5/9` no lo arregla. La captura sin antialiasing (`-aaVector no`) tampoco cambia el resultado.

Limitación probada: con muros como `LINE` sueltas (`pruebas/A_dxf/vivienda_muros_lineas_sueltas.dxf`) `dxf_a_mapa.py` sale con "No se encontró geometría cerrada".

## E. Resultados medidos (`medir_mapa.py`, rejilla de 1 cm de la verdad-terreno)

| Mapa | IoU | Área m² (mapa/verdad) | Espurio m² | Perdido m² | Dist. mapa→verdad máx. | Dist. verdad→mapa máx. | Puertas |
|---|---|---|---|---|---|---|---|
| A1 ezdxf 0,05 | 1,000 | 7,92/7,92 | 0 | 0 | 0 | 0 | 3/3 |
| A1 ezdxf 0,07 (+0,03) | 0,822 | 9,31/7,92 | 0 | 0 | 0,080 | 0,070 | 3/3 |
| A1 ezdxf 0,10 (+0,03) | 0,808 | 9,04/7,92 | 0 | 0 | 0,100 | 0,050 | 3/3 |
| A2 LibreCAD todas las capas | 0,528 | 4,18/7,92 | 0 | 2,79 | 0 | 4,830 | 3/3 |
| A2 LibreCAD solo muros | 0,813 | 7,40/7,92 | 0 | 0 | 0,050 | 0,050 | 3/3 |
| C1 PDF color + muros rellenos (`--auto-origen`) | 0,835 | 7,58/7,92 | 0 | 0 | 0,050 | 0,050 | 3/3 |
| C1 PDF mono, relleno, recortado | 0,100 | 79,42/7,92 | 65,12 | 0 | 2,409 | 0 | 1/3 |
| C1 PDF mono, sin relleno, res 0,01 | 0,042 | 1,04/7,92 | 0,49 | 2,14 | 2,370 | 0,242 | 3/3 · **habitaciones desconectadas** |
| C2 escaneo sin enderezar | 0,576 | 6,90/7,92 | 0 | 0,06 | 0,110 | 0,150 | 3/3 |
| C2 escaneo enderezado (−0,499°) | 0,844 | 7,78/7,92 | 0 | 0 | 0,050 | 0,050 | 3/3 |
| Cadena DXF→map2sdf→sdf2map | 0,288* | 4,45/7,92 | 0 | 0,54 | 0,050 | 0,250* | 3/3 |

\* `sdf2map` devuelve **solo el contorno** del muro grueso (hueco): al comparar solo contornos (borde de la verdad → mapa), media **0,003 m**, p95 0,010 m, máx. **0,014 m**. El valor 0,25 m es el centro del hueco en la esquina. IoU bajo = artefacto de la métrica.
STL generado: mín (0,0,0), máx (10; 8; 2,5) m, 140 triángulos. `gz sdf -k` Valid; `gz sim` 300 iteraciones sin errores (`pruebas/A_dxf/gazebo/log_gzsim.txt`).
Aviso de método: IoU y áreas en celdas gruesas dependen de la cuantización; la métrica fiable es la distancia en metros.

## F. Prueba B — DWG

| Intento | Resultado |
|---|---|
| `librecad dxf2pdf Line_20xx.dwg` (R2000, R2004, R2007, R2010, R2013, R2018; archivos de `test/test-data/` del tarball de LibreDWG, firmas AC1015…AC1032) | ❌ el CLI imprime el uso y **no abre** `.dwg` (solo `<dxf_files>`) |
| Mismos archivos copiados con extensión `.dxf` (diagnóstico, no es un procedimiento) | ❌ sin PDF; el proceso se queda colgado hasta el `timeout` de 60 s |
| LibreCAD con interfaz gráfica abriendo DWG | 🔎 no probado |
| LibreDWG `dwg2dxf` / `dxf2dwg` | 🔎 **no compilado**: el clasificador de permisos bloqueó dos veces ejecutar `colcon build` y `./configure` sobre código descargado en una sesión; fuera del bloqueo solo se extrajo el tarball (sin ejecutar nada) |
| ezdxf con DWG | ❌ no lee DWG; delega en ODA File Converter (propietario, no instalado) |

Documentación consultada (no es prueba): el manual de LibreDWG dice que lee r1.2–r2018 con ~99 % de cobertura y que el escritor es experimental; las fuentes discrepan sobre hasta qué versión escribe. LibreCAD 2.2 se anuncia con lectura DWG básica; no confirma versiones. **No hay un DWG de la vivienda de referencia**: ningún programa instalado puede escribirlo.

## G. Prueba C — PDF

```bash
librecad dxf2pdf -m -s 0.01 -p 420x297 -c -t pruebas/C_pdf/vectorial pruebas/vivienda_3formatos/vivienda.dxf   # -m = monocromo
pdftoppm -r 254 -png vivienda.pdf vivienda_mono
raster_a_mapa.py vivienda_hatch-1.png --m-por-px 0.01 --quitar-texto 60 --res 0.05 --out mapa_hatch_0.05    # muros rellenos en color
# escaneo simulado (fixture, no real): gris, 200 dpi, giro 0,5°, desenfoque, ruido, motas, JPEG q60 -> PDF de solo imagen
pdfimages -list escaneo.pdf          # confirma 1 imagen 3309x2339 a 200 ppi, sin texto ni vectores
pdfimages -all escaneo.pdf extraida
raster_a_mapa.py extraida-000.jpg --m-por-px 0.0127 --abrir 3 --quitar-texto 200 --enderezar --res 0.05 --out mapa_enderezado
```

- El PDF de LibreCAD **no lleva fuentes** (`pdffonts` vacío): el texto va como trazos, así que no se puede filtrar "por texto".
- Colores de capa conservados en el PDF en color: muros negro, cotas rojo, textos azul, puertas verde, mobiliario magenta, eje gris.
- La variante con **muros rellenos** (HATCH sólido sobre cada contorno, misma geometría: `vivienda_hatch.dxf`) funciona sin relleno ni cierres.
- En PDF monocromo, el relleno por recinto cerrado convierte habitaciones enteras en muro porque la hoja y el arco de la puerta (negros) cierran regiones. Sin relleno, solo quedan líneas de 1 cm y símbolos como obstáculos.
- Escaneo: la escala se calculó con 200 ppi y 1:100 (0,0127 m/px). Con una cota real habría que calibrar con `--calibrar`. El giro detectado, −0,499°, coincide con el introducido (0,5°).
- No probados: PDF con capas OCG (pdftoppm no las oculta), escaneos reales, texto vectorizado con `pdftocairo -svg`.

## H. Validación visual en Gazebo (`evidencias/capturas_gazebo/`)

`scripts/lanzar_gazebo_gui.sh pruebas/A_dxf/gazebo/mundo_dxf.sdf pruebas/A_dxf/gazebo/modelos`. Cámara movida con `gz service -s /gui/move_to/pose`. Poses leídas con `gz topic -e -t /world/vivienda_dxf/pose/info`: `suelo` (5,4), `mesa1` (7,5; 6), `silla1` (7,5; 5,2) (`logs/poses_gazebo_gui.txt`).
Con la cámara cenital a yaw 0 el eje X queda hacia arriba (imagen girada 90°); con la cuaternión (−0,5; 0,5; 0,5; 0,5) el norte queda arriba. El plano coincide en ambas.
Incidente: una primera captura con `scrot -u` salió de otra ventana tuya (no del proyecto); se **borró** al instante sin conservarla. Desde entonces solo se captura la región de la ventana de Gazebo con `ffmpeg x11grab` tras comprobar que es la ventana activa.

## I. Otras herramientas (investigación)

- **Dynamic World Generator V2** (`ali-pahlevani/Dynamic_World_Generator`, commit `76bdfc5`, 2026-06-07, MIT): GUI Qt de 3 334 líneas de Python; la búsqueda de `dxf`, `import`, `argparse` y `cv2` en `code/` no encuentra importación de planos ni CLI; solo `sys.argv` para Qt. Muros dibujados a mano; mapa Nav2 propio. Declara Harmonic/Jazzy (afirmación del desarrollador). Sin ventaja para nuestro objetivo.
- **`sherif1152/SDF2MAP`** (hoy `SherifFathey/SDF2MAP`): release `V1.0.0` con un único `sdf2map-linux-x64.tar.gz`; el repositorio contiene `.github docs readme.md scripts`, **sin fuentes ni licencia** (API 404 en `/license`). No se ejecutó (binario opaco). Sin evidencia de ventaja frente a `atinfinity/sdf2map`.
- **Búsqueda de otras alternativas** (Discourse, GitHub, web): no aparece ninguna herramienta que convierta un DXF/PDF directamente a un mundo Gazebo. `rmf_traffic_editor` usa su propio `building.yaml`; `map2gazebo` (ADLINK-ROS) parte de un mapa de ocupación.

## J. Reproducir todo

```bash
cd F1_INVESTIGACION_SOFTWARE && source /opt/ros/jazzy/setup.bash && source ws/install/setup.bash
herramientas/venv/bin/python pruebas/vivienda_3formatos/generar_vivienda.py
# después, los comandos de las secciones D y G
```
Requiere tener `herramientas/` (venv y LibreCAD extraído); no se versiona nada de ahí.

---

# AMPLIACIÓN F1 (2) — PNG, JPG, fotografía simulada y DWG (detalle)

## K. Cambios en los scripts (solo lo necesario)

| Script | Cambio | Por qué |
|---|---|---|
| `scripts/raster_a_mapa.py` | `--ancho-conocido M` | Un PNG no trae escala: equivale a 1 clic de calibración sobre una cota conocida (aquí, la anchura total 10,00 m) |
| idem | `--normalizar` | Quita sombras/luz desigual (gris ÷ fondo desenfocado) antes del umbral; necesario en fotos |
| `scripts/corregir_perspectiva.py` (nuevo, ~60 líneas) | OpenCV: `approxPolyDP` + `getPerspectiveTransform` + `warpPerspective` | Rectificar la foto; no reconoce nada arquitectónico |
| `pruebas/E_jpg/simular_foto.py` | fixture | Simula la foto (no hay foto real) |
| `scripts/compilar_libredwg.sh` | verifica la firma y compila | Procedimiento reproducible de DWG |

## L. Prueba 1 — PNG de plano con anotaciones

Exportación: LibreCAD `dxf2pdf` (1:100, A3) → `pdftoppm -r 100 -png -singlefile` → `pruebas/D_png/plano_{hatch,contorno}_{color,mono}.png` (1655 × 1170 px, 100 dpi; 1 px = 2,54 cm nominal). Cuatro variantes: muros rellenos/contorno × color/monocromo. Contienen muros, puertas (hoja y arco), mobiliario, cotas, textos y eje, como un plano real.

```bash
# color + muros rellenos: filtro de color y calibración con la anchura total
raster_a_mapa.py plano_hatch_color.png --ancho-conocido 10.0 --quitar-texto 20 --res 0.05 --out mapas/hatch_color
# monocromo + muros rellenos: --abrir 3 borra lo más fino que un muro (cotas, textos, arcos)
raster_a_mapa.py plano_hatch_mono.png  --ancho-conocido 10.0 --abrir 3 --quitar-texto 20 --res 0.05 --out mapas/hatch_mono
medir_mapa.py mapas/hatch_mono.yaml --auto-origen --json mapas/hatch_mono.json
```

| Variante | Escala usada | IoU | Área mapa/verdad m² | Espurio m² | Perdido m² | Dist. máx. mapa→verdad | Dist. máx. verdad→mapa | Puertas |
|---|---|---|---|---|---|---|---|---|
| Relleno + color | 0,02532 m/px (cota) | 0,852 | 9,29/7,92 | 0 | 0 | 0,050 | 0,000 | 3/3 |
| Relleno + mono, con `--abrir 3` | 0,02532 | 0,851 | 9,30/7,92 | 0 | 0 | 0,050 | 0,000 | 3/3 |
| Relleno + mono, **sin limpieza** | 0,0254 (nominal) | 0,054 | 5,31/7,92 | **4,43** | 5,61 | 2,200 | 2,200 | 3/3 |
| Contorno + color (`--cerrar 3 --rellenar`) | 0,02532 | 0,615 | 7,08/7,92 | 0 | 0,61 | 0,050 | 1,860 | 3/3 |
| Contorno + mono (`--cerrar 3 --rellenar`) | 0,0254 | 0,081 | 68,92/7,92 | 58,18 | 1,77 | 2,409 | 1,269 | 1/3 |

- **Escala:** el nominal 0,0254 m/px y el calibrado 0,02532 difieren un 0,3 % (la caja de tinta incluye 1 px de línea). Las dos dimensiones (10,000 × 8,000 m) salen isótropas con una sola cota.
- **Texto y cotas como obstáculos:** sí, sin limpieza en monocromo (fila 3: 4,43 m² espurios; además arrastran el recuadro y descuadran escala y origen). Con filtro de color o `--abrir` desaparecen.
- La sobreárea (9,3 frente a 7,9 m²) no es error de posición: es la cuantización de los muros de 2 y 4 celdas con el umbral del 49 %; la distancia máxima sigue en 0,05 m.

## M. Prueba 2 — JPG y fotografía simulada

**JPG** (`pruebas/E_jpg/plano_hatch_{color,mono}_q{90,75,40}.jpg`, 46–40 KB):

| Entrada | Parámetros | IoU | Perdido m² | Dist. máx. verdad→mapa | Puertas |
|---|---|---|---|---|---|
| Mono q90/q75/q40 | `--abrir 3` | 0,851 | 0 | 0,000 | 3/3 |
| Color q40 / q75 / q90 | filtro de color por defecto | 0,835/0,827/0,830 | 0,04/0,10/0,08 | 0,31/0,43/0,35 | 3/3 |
| Color q75, `--sat-max 90` y `130` | — | 0,827/0,828 | 0,10/0,09 | 0,43/0,41 | 3/3 |
| **Color q75, gris + `--abrir 3`** (`--sat-max 255`) | recomendado | **0,852** | **0** | **0,050** | 3/3 |

La pérdida de color estaba entre x ∈ [1,77; 9,99] y y ∈ [0,01; 4,05], cerca de símbolos de color; la causa es el submuestreo de croma del JPEG. No la corrige subir la saturación; sí ignorar el color.

**Foto simulada** (`pruebas/E_jpg/simular_foto.py` sobre `hoja_200dpi.png`; lienzo 4000 × 3000, mesa de madera, gradiente de luz, desenfoque σ 1,4, ruido σ 6, JPEG q75). Esquinas reales de la hoja: leve `(520,330) (3560,520) (3820,2650) (330,2480)`; fuerte `(900,260) (3500,700) (3750,2800) (250,2300)` (+ sombra).

```bash
corregir_perspectiva.py foto_simulada_fuerte.jpg --out foto/rect_auto_fuerte        # --papel 420x297 --escala 100 --px-por-mm 8
raster_a_mapa.py foto/rect_auto_fuerte.png --m-por-px 0.0125 --normalizar --sat-max 255 --abrir 5 --quitar-texto 100 --res 0.05 --out foto/mapa_auto_fuerte_papel
```

| Caso | Esquinas / escala | Dimensiones medidas | Dist. máx. mapa→verdad / verdad→mapa | Puertas |
|---|---|---|---|---|
| Leve, auto, escala por la hoja | detectadas `(520,333) (3559,520) (3818,2647) (333,2478)` | 10,013 × 8,013 m | 0,050 / 0,070 | 3/3 |
| Fuerte, auto, escala por la hoja | `(900,262) (3498,698) (3749,2797) (254,2298)` | 10,013 × 8,013 m | 0,050 / 0,070 | 3/3 |
| Leve y fuerte, auto + cota 10,0 m | — | 10,000 × 8,002 m | 0,050 / 0,050 | 3/3 |
| Fuerte, 4 clics **fuera** de la hoja (±10 px) | manual | 42,0 × 29,7 m (entra la mesa) | 0,25 / **7,94** | 2/3 ❌ |
| Fuerte, 4 clics **dentro** (15 px) | manual | 10,113 × 8,113 m | 0,10 / 0,15 | 3/3 |
| Idem + cota 10,0 m | manual | 10,000 × 8,022 m | 0,050 / 0,050 | 3/3 |
| **Sin corregir perspectiva** (leve / fuerte) | cota 10,0 m | — | 1,60 / 2,25 · 1,60 / 2,58 | — ❌ |

Los errores se miden en metros contra `verdad_terreno_muros_1cm.npy` (la misma geometría del DXF). Solo se probó el caso en que la **hoja completa** sale en la foto y la imagen tiene suficiente resolución (≈ 1,4 cm/px nativos en el plano). El plano ocupa ~25 % de la hoja.
Figura: `evidencias/figuras/foto_perspectiva_proceso.png`.

## N. Prueba 3 — DWG con LibreDWG

**Procedencia (revisada antes de compilar).**

| Comprobación | Resultado |
|---|---|
| Tarball descargado en la sesión anterior `0.13.4.8043` | Es una **prerrelease** (`prerelease: true`), construida por `github-actions[bot]`, **sin firma**. SHA-256 coincidía con `dist.sha256`, pero ese archivo lo genera el mismo bot. **Descartada para compilar.** |
| Release oficial GNU `libredwg-0.14.tar.xz` | Descargada de `https://ftp.gnu.org/gnu/libredwg/` con su `.sig` y `gnu-keyring.gpg` |
| Firma | `gpgv`: *Good signature* de `Reini Urban <reini.urban@gmail.com>`, clave RSA `38A4167B0DB69E49C5F7216CB8C28866AB27A7A2`, fechada el 31-08-2026 |
| SHA-256 del tarball | `62ebb73b984f865960f20ed26619ea5f8789d5e3fd088fa40a2598384da81275` |
| Contenido | 1138 archivos; sin `.so/.a/.o/.exe/.dll/.dylib`; sin `curl/wget/git clone/pip/sudo` en `configure`, `configure.ac`, `Makefile.*`, `autogen.sh` (solo un `dnl` sobre `npm` en `configure.ac:946`, comentario de pruebas) |
| Licencia | GPL-3 (README); mantenedor y contacto de seguridad: Reini Urban |
| Dependencias | Solo compilador C y `make`; `pcre2` opcional (solo `dwggrep`) |
| Instrucciones oficiales | `README`/`configure.ac`: opciones `--disable-bindings`, `--disable-docs`, `--disable-python`; escritor activo por defecto |

**Compilación** (`scripts/compilar_libredwg.sh`): `gpgv` → `./configure --disable-bindings --disable-docs --disable-python` → `make -j$(nproc)`. Sin `sudo`.
`make install --prefix=<ruta de F1>`: **falla** (`target 'SOCIALTECH/F1_.../libredwg.so.0.0.14': No such file or directory`) por el espacio de `MAPA SOCIALTECH`. No se insistió: los programas funcionan desde `herramientas/libredwg_gnu/libredwg-0.14/programs/` (`dwg2dxf --version` → `0.14`). Quedaron creadas `herramientas/libredwg/lib` vacía y se eliminó.

**Lectura (DWG → DXF)** de los archivos de prueba del propio proyecto (`test/test-data/<versión>/{Line,Polyline,Arc}.dwg`, firmas `AC1015…AC1032`; no se ha comprobado con qué programa se crearon):

```bash
dwg2dxf -y -o Line_2007.dxf Line_2007.dwg
```
- 18 archivos, **18 con código 0**. R2007: 2 mensajes `ERROR` no fatales (`Invalid num_pages 0`, `Preview overflow`), de la imagen de vista previa.
- `ezdxf` lee los 18. Línea: `(21,608; 2,812; 0) → (11,031; 16,638; 0)`; arco: centro `(-18,193; 6,687)`, r 8,293, 114,73°→87,02°; polilínea idéntica. **Misma geometría en las seis versiones**.
- Dibujo complejo `example_{2000,2004,2007,2010,2013,2018}.dwg` (146–582 KB): conversión correcta en las seis (R2013/R2018 dejan 6 mensajes de error no fatales en el log); `ezdxf` los lee; todos dan **66 entidades**, 4 capas usadas, `INSUNITS=4` (mm), la misma extensión y el mismo reparto de tipos (11 `LWPOLYLINE`, 10 `INSERT`, 9 `DIMENSION`, 8 `LINE`…). No se comparó con una verdad externa.

**Vivienda** (`pruebas/B_dwg/vivienda/`):

| Paso | Resultado |
|---|---|
| `dxf2dwg --as r2000 original.dxf` | ❌ `Invalid DXF code 50 for MTEXT` / `Failed to decode DXF file`: LibreDWG no acepta el MTEXT de las 2 cotas que escribe `ezdxf`. **No se generó DWG.** |
| Mismo DXF sin las 2 `DIMENSION` y sus bloques `*D*` (`sin_cotas.dxf`) | ✅ `vivienda.dwg`, firma `AC1015` (R2000), 21 298 B. Avisos: `Duplicate handle`, `MLEADERSTYLE unsupported` |
| `dwg2dxf vivienda.dwg` | ✅ 0 errores. `ezdxf` avisa de un handle repetido y de un `ENDBLK` suelto y los corrige |
| Comparación original ↔ ida y vuelta | Entidades idénticas (9 `LWPOLYLINE`, 3 `LINE` + 3 `ARC` de puertas, 2 `INSERT`, 4 `TEXT`, 1 `LINE` de eje); capas `A-*` conservadas; `INSUNITS=4`; **vértices de los 9 muros idénticos** |
| `dxf_a_mapa.py` sobre el DXF resultante | 200×160 px, 10,000 × 8,000 m, origen (0,0); IoU 1,000; `cmp` → **idéntico byte a byte** al mapa obtenido del DXF original; puertas 3/3 |

Limitaciones: (1) el DWG de la vivienda lo escribe LibreDWG, no AutoCAD; (2) el escritor solo ofrece R2000 en esta prueba (README: R2010–R2018 dan errores de CRC); (3) las cotas hubo que quitarlas para poder escribirlo; (4) la lectura se valida por coherencia entre versiones, no contra un archivo de IQS.
LibreCAD sigue sin servir para DWG por CLI (sección F).

## O. Reproducción rápida

```bash
cd F1_INVESTIGACION_SOFTWARE
scripts/compilar_libredwg.sh                                  # firma + build (≈ minutos)
LW=herramientas/libredwg_gnu/libredwg-0.14/programs
"$LW/dwg2dxf" -y -o plano.dxf plano.dwg                       # DWG -> DXF
herramientas/venv/bin/python scripts/dxf_a_mapa.py plano.dxf --capas A-MUROS --res 0.05 --out mapa
ros2 run map2sdf map2sdf --map mapa.yaml -o salida --format model --wall-height 2.5 --world-name vivienda
# raster: scripts/raster_a_mapa.py (calibrar con --ancho-conocido o --m-por-px); foto: scripts/corregir_perspectiva.py antes
```
