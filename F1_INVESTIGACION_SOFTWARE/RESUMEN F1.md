# RESUMEN F1 — Investigación de software open source plano → Gazebo + mapa

**Estado:** ✅ CERRADA (2026-11-07, autorizada por José Ángel) · Solución: `map2sdf` + `sdf2map` · Formatos probados: DXF, DWG, PDF, PNG, JPG, foto simulada · **Plan:** `../PLAN_MAPA_SOCIALTECH.md`
**Anexo con comandos, medidas y citas:** `evidencias/DETALLE F1.md`
Leyenda: ✅ confirmado con prueba · 🔎 por comprobar · ❌ fallido · ➖ no aplicable / no probado

## 1. Conclusión

**Solución elegida (provisional): `map2sdf` + (opcional) `sdf2map`, ambos de atinfinity, Apache-2.0.**

```
plano 2D (PNG/PGM + YAML nav2)
   │  map2sdf --format model
   ▼
modelo base de muros (STL + model.sdf, origen del YAML)  ──┐
mesa/silla/puerta de 2025 (<include> + pose)  ─────────────┴─► mundo Gazebo Harmonic
```

- **Mundo 3D:** `map2sdf` convierte el plano en un modelo de muros listo para `<include>`, justo la separación "aula base + objetos" de 2025.
- **Mapa para RViz2:** el plano de entrada ya es un mapa nav2. Para el mapa **con mobiliario** se genera con `sdf2map` desde el mundo completo.
- **Reserva:** `world_creator` de linorobot2 (GUI, mismo principio de STL). Es manual, así que no encaja con "todo desde el plano".
- Código propio previsto: ninguno de conversión. Solo un `launch.py` y un script de ensamblado del mundo.

## 2. Comparativa (matriz resumida)

| | map2sdf | sdf2map | linorobot2 `world_creator` | image2gazebo | scenery_builder | rmf_traffic_editor |
|---|---|---|---|---|---|---|
| Commit | `fde43ff` | `66feb61` | `f6b0bd0` (jazzy) | `8f53ec2` | `b0e7abe` | `9cb2a6b` |
| Último cambio | 2026-07-11 | 2026-07-10 | 2026-09-29 | 2022-04-20 | 2026-09-24 | 2026-11-03 |
| Licencia | Apache-2.0 | Apache-2.0 | Apache-2.0 | MIT | sin LICENSE en la raíz 🔎 | Apache-2.0 |
| Entrada | mapa nav2 (YAML+PGM/PNG) | mundo SDF | imagen o mapa nav2, vía GUI | PNG | DSL propio (FloorPlan) | `building.yaml` (GUI) |
| Salida | modelo/mundo SDF + STL | mapa PCD + PGM/YAML | modelo+mundo SDF + STL | modelo + STL | SDF, mapa, mallas | mundos Gazebo/Ignition |
| Instala en Jazzy | ✅ | ✅ | ✅ | ➖ pide `sudo apt` | ➖ pide Python 3.11 + Blender | ➖ no probado |
| Funciona en Harmonic | ✅ | ✅ | 🔎 no ejecutado (GUI) | ➖ | ➖ | 🔎 solo cita Ignition |
| Automático (sin clics) | ✅ | ✅ | ❌ GUI | ✅ | ✅ tras describir a mano | ❌ GUI |
| Escala/origen | del YAML | del SDF | clics o YAML | parámetro | del DSL | del editor |

## 3. Pruebas realizadas (plano sintético 10 × 8 m, 0,05 m/px, 3 huecos de puerta)

| Prueba | Resultado |
|---|---|
| Compilar `map2sdf`, `sdf2map`, `linorobot2_gazebo` en un espacio aislado | ✅ |
| `map2sdf`: PNG → SDF + STL | ✅ 142 triángulos |
| Geometría del STL | ✅ 10,0 × 8,0 × 2,5 m, origen (0, 0) exacto |
| `gz sdf -k` sobre el mundo generado | ✅ `Valid.` |
| Mundo cargado en Gazebo Harmonic (servidor, 500 iteraciones) | ✅ sin errores ni avisos |
| Mundo = muros + mesa + silla de 2025 por `<include>` | ✅ válido y carga sin errores |
| `sdf2map`: mapa de ocupación del mundo completo | ✅ mueble aparece en la zona esperada |
| Huecos de puerta conservados en el mapa regenerado | ✅ los 3 siguen libres |
| Precisión del mapa regenerado frente al plano | ⚠️ desviación media 0,3–0,6 px, máx. ≈ 2 px (≈ 10 cm) |
| Vista en la interfaz gráfica de Gazebo, colisión con robot | 🔎 no comprobado |

## 4. Limitaciones y avisos medidos

1. **`sdf2map` engorda los muros ≈ 1 celda por lado** con el cierre por defecto (`--grid-close 1`). Con `--grid-close 0` salen huecos. Por eso, **para paredes conviene usar el plano original como mapa** y `sdf2map` solo para sumar mobiliario.
2. El mapa regenerado queda con otro tamaño y origen (203×163 celdas, origen −0,05) que el plano: hay que registrar el origen real.
3. En `map2sdf` el origen sale del YAML: **la fila 0 del PNG es el borde superior (y máximo)**. Un plano dibujado al revés sale invertido. Me pasó en mi propia prueba.
4. La documentación de linorobot2 aún llama `image_to_gazebo` a lo que ahora es `world_creator`.
5. Muebles de 2025: probados solo `table1` y `chair` (la silla tiene 155 000 caras, como ya vimos en F0). El rendimiento de `sdf2map` con la malla fue aceptable.
6. `scenery_builder` y `rmf_traffic_editor` **no se han probado**: se descartan por entrada incompatible con "todo desde el plano" y por coste de instalación, no por un fallo observado.

## 5. Pendiente y decisiones para ti

- **Autorizar el cierre de F1** o pedirme más pruebas (p. ej. abrir la GUI de Gazebo, probar `world_creator`, o un plano real con puertas).
- Confirmar que el **plano de entrada del equipo** será una imagen en formato nav2 (PNG/PGM + YAML) o indicar el formato real (DXF, PDF…). Si no es imagen, hace falta un paso previo que aún no he investigado.
- El **espesor de los muros** del plano real condiciona la precisión: con 0,05 m/px, un muro de 0,10 m son solo 2 píxeles.

**Evidencias (`evidencias/`):** `DETALLE F1.md`, `comparacion_plano_vs_mapa.png`, `logs/`. Pruebas y salidas completas en `pruebas/`, repos clonados sin modificar en `repos/`.

---

# AMPLIACIÓN F1 — Conversión de DXF, DWG y PDF

**Objetivo real:** recibir un plano arquitectónico (DXF, DWG o PDF) y llegar al mundo Gazebo y al mapa RViz2 con el mínimo trabajo manual. Todo se probó con **una misma vivienda sintética** (10 × 8 m, muros de 0,20 y 0,10 m, 3 puertas de 0,90 m, mobiliario, cotas, textos, eje) generada una sola vez (`pruebas/vivienda_3formatos/`). **No son datos de IQS.** Los errores se dan en **metros** contra la verdad-terreno, no en píxeles.

## 1. Respuestas a tus 9 preguntas

| # | Pregunta | Respuesta (con su estado) |
|---|---|---|
| 1 | ¿Qué herramienta convierte un DXF en mapa para map2sdf? | **`ezdxf`** (MIT) con un script mío de 70 líneas (`scripts/dxf_a_mapa.py`): lee capas y unidades, rellena polígonos, escribe PGM+YAML. ✅ error 0 con celda de 5 cm y ≤ 1 celda con celdas que no cuadran. |
| 2 | ¿Y si entregan un DWG? | **No verificado.** Procedimiento: pedir DXF a quien lo exporta; si no, `dwg2dxf` de LibreDWG (GPL-3, descargado y con SHA-256 correcto, **sin compilar**). El CLI de LibreCAD **no** abre `.dwg`. 🔎 bloqueado (§7). |
| 3 | ¿PDF vectorial o escaneado? | Vectorial: `pdftoppm` + `raster_a_mapa.py`. ✅ solo si los **muros van rellenos y con color propio**. Escaneado: + enderezado y calibración. ✅ solo en el caso favorable simulado. ❌ en PDF monocromo con contornos. |
| 4 | ¿Qué formato exige menos trabajo manual? | **DXF con capas** ≫ PDF vectorial en color con muros rellenos > PDF escaneado. DWG añade un paso. |
| 5 | ¿Se conservan las dimensiones? | DXF: ✅ exactas (unidades leídas de `$INSUNITS`, origen CAD conservado). PDF: ✅ pero **depende de la escala de impresión o de una cota conocida** y se pierde el origen CAD. |
| 6 | ¿Se mantienen las puertas abiertas? | ✅ en todas las rutas que funcionan (3/3), **si el plano dibuja el hueco en el muro**. No probado con muros continuos y puerta como bloque. |
| 7 | ¿Mundo Gazebo y mapa RViz2? | ✅ Gazebo (GUI) y ✅ mapa PGM+YAML nav2 desde el mismo DXF. 🔎 Visualizarlo en RViz2 no se ha hecho aquí (F3). |
| 8 | ¿Hay algo open source mejor? | **No.** Ninguna alternativa investigada importa planos ni mejora a `map2sdf` + `sdf2map` (§3). Se mantiene. |
| 9 | ¿Se reutilizan los modelos de SocialTech? | ✅ `table1` y `chair` de 2025 cargan por `<include>` en las poses pedidas. ⚠️ El origen del modelo no es el centro del mueble (ver §4). |

## 2. Rutas probadas con la misma vivienda (error medido en metros)

| Ruta | Resultado | Error máx. vs CAD | Puertas | Intervención |
|---|---|---|---|---|
| **A1 DXF → `ezdxf` → mapa** (0,05 m) | ✅ | **0 m** (cotas múltiplo de celda) | 3/3 | Nombrar la capa de muros |
| A1 con celda de 0,07 y 0,10 m | ✅ | 0,08 y 0,10 m (= 1 celda) | 3/3 | — |
| **A2 DXF → LibreCAD (`dxf2pdf`) → `pdftoppm` → mapa**, todas las capas, muros como contorno | ❌ | pierde 2,79 m² de muro (IoU 0,53) | 3/3 | La hoja de la puerta dibujada encima rompe el contorno |
| A2 con solo la capa de muros (filtrada con ezdxf) | ✅ | 0,05 m | 3/3 | Filtrar capas antes |
| **C1 PDF vectorial en color, muros rellenos** | ✅ | 0,05 m | 3/3 | Escala de impresión o cota |
| C1 PDF vectorial **monocromo**, contornos | ❌ | 58–65 m² de obstáculos espurios | 1/3 | Inviable sin limpieza manual |
| **C2 PDF escaneado (simulado)**, muros rellenos, enderezado | ✅ (caso favorable) | 0,05 m | 3/3 | Enderezar, calibrar |
| C2 sin enderezar (giro 0,5°) | ⚠️ | 0,11–0,15 m | 3/3 | — |
| **B DWG** | 🔎 no ejecutado | — | — | Bloqueado |
| **Cadena completa DXF → map2sdf → Gazebo → sdf2map** | ✅ | contorno: media 3 mm, máx. 1,4 cm | 3/3 | — |

Figura: `evidencias/figuras/comparacion_rutas_dxf_pdf.png`. IoU bajo (0,8) en muros finos es cuantización, no error físico.

## 3. Herramientas investigadas

| Herramienta | Licencia | Veredicto |
|---|---|---|
| **ezdxf** 1.4.5 | MIT | ✅ **Elegida** para DXF: capas, polilíneas, bloques, unidades. No lee DWG sin ODA. |
| **LibreCAD** 2.2.0.2 (apt, sin instalar) | GPL-2 | ⚠️ Solo CLI `dxf2pdf` (no hay `dxf2png`; escala y papel sí configurables). No selecciona capas por CLI. DWG: el CLI no lo abre. |
| **poppler** (`pdftoppm`, `pdfimages`) | GPL | ✅ Rasterizar y extraer imágenes de PDF. |
| **LibreDWG** 0.13.4.8043 | GPL-3 | 🔎 `dwg2dxf` lee hasta R2018 (según su manual); escritor experimental. No compilado. |
| ODA File Converter | Propietaria | ❌ No instalado (tu regla). |
| **Dynamic World Generator V2** | MIT | ❌ GUI Qt; **sin importar planos ni CLI** (comprobado en su código, 3 334 líneas). Sin ventaja sobre `map2sdf`. |
| `sherif1152/SDF2MAP` (hoy `SherifFathey`) | **Sin licencia** | ❌ Solo binario precompilado sin fuentes; **no ejecutado**. Hace lo mismo que `atinfinity/sdf2map`. |
| `map2gazebo` (ADLINK) | — | ➖ Mismo principio que `map2sdf`; solo citado para ROS 2 Foxy. |

Distinción de fuentes: lo marcado ✅/❌ lo medí yo; lo marcado 🔎 es documentación o afirmación del desarrollador.

## 4. Validación visual en Gazebo Harmonic (hecha)

Capturas en `evidencias/capturas_gazebo/` (cenital con norte arriba, oblicua, puerta P1, mobiliario).
- ✅ Paredes, suelo y **las 3 aberturas** visibles y abiertas; orientación coincide con el CAD (con el norte arriba).
- ✅ Dimensiones: el STL mide 10,0 × 8,0 × 2,5 m (medido); la vista gráfica es cualitativa.
- ✅ `mesa1` en (7,5; 6,0) y `silla1` en (7,5; 5,2) leídas del simulador.
- ⚠️ La mesa de 2025 se ve desplazada del punto indicado: **su origen de modelo no es su centro**. Para el mobiliario habrá que registrar el desfase de cada modelo (F4).
- ⚠️ Los muros salen grises y sin material; la altura (2,5 m) es parámetro, no dato del plano.

## 5. map2sdf + sdf2map frente a las alternativas

Se **mantiene**. Ninguna alternativa ofrece algo que ellos no hagan, y ninguna importa planos. No se cambia de tecnología.

## 6. Limitaciones medidas y abiertas

1. **Muros como líneas sueltas** (doble línea sin cerrar): `dxf_a_mapa.py` aborta con "No se encontró geometría cerrada" (probado). Hay que cerrarlos en el CAD o añadir un paso de polígonos (no desarrollado; por probar).
2. **`sdf2map` devuelve los muros gruesos huecos** (solo el borde); el contorno coincide a 1,4 cm. Para navegación basta; para áreas, no.
3. **PDF**: se pierde el origen CAD, la escala depende de la impresión y los símbolos de puerta rompen contornos.
4. **`sdf2map`** engorda muros finos una celda (§ resumen anterior). Preferir el mapa del plano para paredes.
5. Mi plano dibuja el hueco de puerta en el muro. Un plano con muros continuos no daría puertas abiertas sin cortarlas.

## 7. Pendiente y bloqueado

- **DWG (prueba B): no ejecutada.** El sistema bloqueó dos veces compilar código externo. Para continuar, ejecuta tú:
  `! cd "/home/jose-angel/Desktop/MAPA SOCIALTECH/F1_INVESTIGACION_SOFTWARE/herramientas/libredwg_src" && tar xzf libredwg-0.13.4.8043.tar.gz && cd libredwg-0.13.4.8043 && ./configure --prefix="$PWD/../../libredwg" --disable-bindings --disable-docs && make -j4 && make install`
  Con eso pruebo `dwg2dxf` sobre DWG reales (R2000–R2018, ya extraídos) y `dxf2dwg` para fabricar el DWG de la vivienda.
- Interfaz gráfica de LibreCAD con DWG; PDF con capas OCG; escaneos reales; planos con muros continuos.
- RViz2 mostrando el mapa generado (F3).

## 8. Recomendación

**Pedir a IQS el plano en DXF, con los muros en una capa propia y como contornos cerrados.** Con DXF: `ezdxf` → mapa → `map2sdf` → Gazebo, y `sdf2map` para sumar mobiliario. Si solo hay DWG, exportar a DXF (LibreDWG, por verificar). Si solo hay PDF, aceptarlo únicamente si es vectorial con muros rellenos y de color propio; un PDF monocromo o escaneado exige limpieza manual. **F1 sigue abierta; no avanzo a F2 sin tu autorización.**

> Nota posterior: el bloqueo de DWG (§7) ya está resuelto, ver la ampliación (2).

---

# AMPLIACIÓN F1 (2) — PNG, JPG, fotografía y DWG

Misma vivienda de 10 × 8 m y misma verdad-terreno que antes. Errores en **metros**. Los procedimientos ya verificados no se repiten.

## 1. Tabla definitiva de formatos

| Formato de entrada | Herramienta | Estado | Error máx. medido | Puertas | Qué hace falta |
|---|---|---|---|---|---|
| **DXF** (capas, contornos cerrados) | `ezdxf` + `dxf_a_mapa.py` | ✅ **Verificado** | 0 m (celda 5 cm); ≤ 1 celda en general | 3/3 | Indicar la capa de muros |
| **DWG** | **LibreDWG 0.14** `dwg2dxf` → DXF → lo anterior | ✅ **Verificado con limitaciones** | 0 m (mapa idéntico al del DXF) | 3/3 | Pasar a DXF primero |
| **PDF vectorial en color, muros rellenos** | `pdftoppm` + `raster_a_mapa.py` | ⚠️ Con limitaciones | 0,05 m | 3/3 | Escala de impresión o 1 cota |
| PDF vectorial monocromo o muros en contorno | idem | ❌ No funciona sin limpieza manual | 2,4 m; 58–65 m² espurios | 1/3 | Redibujar o pedir DXF |
| PDF escaneado | + enderezado | ⚠️ Solo caso simulado favorable | 0,05 m (sin enderezar 0,15) | 3/3 | Enderezar, calibrar, muros rellenos |
| **PNG limpio** (mapa de ocupación) | `map2sdf` directo | ✅ **Verificado** (1ª prueba de F1) | 0 | 3/3 | Nada |
| **PNG de plano con cotas y textos**, muros rellenos | `raster_a_mapa.py` | ⚠️ Con limitaciones | **0,05 m** | 3/3 | Calibrar con 1 cota; gris + `--abrir 3` |
| PNG con cotas, muros en **contorno**, color | idem | ⚠️ Pierde 0,61 m² de muro | 0,05 m (pero 1,86 m de hueco) | 3/3 | Cerrar contornos a mano |
| PNG con cotas, muros en contorno, **monocromo** | idem | ❌ No funciona | 2,4 m; 58 m² espurios | 1/3 | Inviable |
| **JPG** (q 40–90), muros rellenos | idem | ⚠️ Con limitaciones | **0,05 m** (con gris + `--abrir`) | 3/3 | Igual que PNG; ignorar el color |
| **Foto con perspectiva** (simulada), muros rellenos | OpenCV (`corregir_perspectiva.py`) + lo anterior | ⚠️ Solo simulación | **0,07 m** (auto) | 3/3 | Hoja completa y plana en la foto |
| Foto **sin** corregir la perspectiva | — | ❌ No funciona | 1,6–2,6 m | — | Corregir siempre |

Leyenda: ✅ verificado · ⚠️ funciona con condiciones · ❌ no funciona. Las simulaciones **no son fotos reales**.

## 2. Lo que sale de las pruebas nuevas

**PNG con anotaciones (100 dpi, A3, 1:100).** Con muros rellenos el error es de una celda (0,05 m) y **no hay obstáculos falsos** *si se limpia*. Sin limpieza, en monocromo, cotas y textos sí se vuelven obstáculos (4,43 m² espurios, 5,61 m² de muro perdido). En color basta un filtro de color; en monocromo, `--abrir 3` borra todo lo más fino que un muro. Con muros dibujados como contorno, vuelve el fallo de siempre (la hoja de la puerta rompe el contorno).

**JPG.** Con calidades 90, 75 y 40 funciona igual que el PNG. En color aparecía una pérdida de hasta 0,4 m de un tramo de muro por el submuestreo de croma; se elimina trabajando en **gris + `--abrir`** (queda a 0,05 m, 0 pérdidas).

**Fotografía simulada** (hoja A3 en perspectiva, luz desigual, sombra, ruido, JPEG q75; dos niveles):
- Detección automática de las esquinas con OpenCV estándar (`approxPolyDP`): acierta a ≤ 3 px.
- **Escala solo por la hoja** (A3 a 1:100): 10,013 × 8,013 m, es decir 1,3 cm de error sobre 10 m, sin usar ninguna cota. Con una cota conocida: 10,000 × 8,002 m.
- Error máximo del mapa: 0,07 m en ambos niveles. Sin corregir la perspectiva: 1,6–2,6 m.
- Con 4 clics manuales: si caen **fuera** de la hoja, entra la mesa y falla; **dentro** del borde (15 px) la escala se desvía un 1,1 %, y calibrando con la anchura queda en 0,05 m.
- No se desarrolló ningún reconocimiento arquitectónico: solo `getPerspectiveTransform`, `warpPerspective` y `approxPolyDP`.

**DWG.** Procedencia revisada antes de compilar: **la versión descargada antes era una prerrelease de CI sin firma**, así que se descartó y se usó la **release oficial 0.14 de GNU**, con **firma GPG válida** de su mantenedor (llavero oficial de GNU), sin binarios precompilados y sin red ni `sudo` en el build.
- Compilación en `herramientas/` (sin instalar nada). `make install` falla porque la ruta tiene un espacio (`MAPA SOCIALTECH`); no hace falta, los programas se usan desde el árbol de compilación.
- **Lectura:** `dwg2dxf` convierte R2000, R2004, R2007, R2010, R2013 y R2018 y las **seis versiones dan exactamente la misma geometría** (línea, polilínea y arco a 3 decimales). Dibujo complejo `example_20xx.dwg`: 66 entidades, cotas, bloques, mm: idéntico en las seis versiones.
- **Vivienda:** DXF → DWG R2000 (`dxf2dwg`) → DXF: 9 muros con vértices idénticos, 6 capas, bloques y `INSUNITS=4` conservados. El mapa resultante es **idéntico byte a byte** al del DXF.

## 3. Respuestas a lo que pedías documentar

1. **Qué funciona realmente:** DXF y DWG (vía DXF) sin pérdida; PNG, JPG y PDF vectorial solo con muros rellenos y limpieza.
2. **Qué necesita limpieza previa:** todo lo raster (PNG, JPG, PDF, foto): calibrar, quitar texto y cotas, y la foto además rectificarla.
3. **Escala:** DXF/DWG la traen en las unidades (`$INSUNITS`; si falta el script **aborta**). En raster se calibra con **una distancia conocida** (cota o ancho total) o con la escala de impresión y el tamaño de hoja.
4. **Cómo se identifican las paredes:** en DXF/DWG, por **nombre de capa**; en raster, por **tinta oscura, sin saturación y gruesa** (los muros rellenos son más gruesos que cotas, textos y símbolos).
5. **Puertas abiertas:** se mantienen **si el plano dibuja el hueco en el muro**. Nada detecta puertas; los huecos pasan tal cual. Un plano con muros continuos y puerta como bloque no daría puertas abiertas (sin probar).
6. **Correcciones manuales:** nombrar la capa (DXF/DWG); una cota o el ancho total (raster); en foto, comprobar las esquinas de la hoja; cerrar contornos o rellenar muros si el CAD los dibuja huecos.
7. **Limitaciones:** ver la tabla. Las de DWG: el escritor de LibreDWG solo crea R2000 y su lector DXF rechazó el texto de cotas que escribe `ezdxf` (hubo que quitar las cotas para fabricar el DWG de prueba); los DWG de prueba no son de AutoCAD con la vivienda.

## 4. Lo que NO se ha podido comprobar

- Un DWG **creado por AutoCAD** con la vivienda: ningún programa del equipo lo escribe. La lectura se apoya en las muestras del proyecto (seis versiones, geometría coherente) y no en un archivo de IQS.
- Fotos y escaneos **reales**; PDF con capas OCG; planos con muros continuos; DXF con muros como líneas sueltas (probado: aborta con mensaje claro).
- RViz2 mostrando el mapa (F3).

## 5. Propuesta de cierre definitivo de F1

**Solución:** `map2sdf` + `sdf2map` (sin cambios; ninguna incompatibilidad importante). Entrada preferente: **DXF**, o **DWG** convertido con `dwg2dxf` de LibreDWG. Raster/PDF/foto: solo como plan B y con muros rellenos.

**Pedir a IQS:** el plano en DXF o DWG, con los muros en una capa propia y como contornos cerrados, huecos de puerta abiertos en el muro y **unidades en el archivo**. Si solo hay PDF o imagen, pedir que los muros vayan **rellenos** y una cota para calibrar.

**Qué queda para F2:** convertir un plano de vivienda real con este procedimiento, comprobar el rendimiento de las sillas y registrar los desfases de origen de los modelos de 2025.

**F1 cerrada con tu autorización. F2 no iniciada.**

---

# CIERRE DE F1 E INDICACIONES PARA F2

**F1 cerrada el 2026-11-07.** Entregables: este resumen, `evidencias/DETALLE F1.md`, scripts en `scripts/`, pruebas en `pruebas/` y figuras y capturas en `evidencias/`. Los repositorios de terceros están en `repos/`, sin modificar, y `herramientas/` (venv, LibreCAD extraído, LibreDWG compilado) no forma parte del entregable.

**Indicaciones para F2 (`F2_PLANO_SIMPLE_GAZEBO/`):**
1. Leer primero `PLAN_MAPA_SOCIALTECH.md`, `F0.../RESUMEN F0.md` y este `RESUMEN F1.md`; no repetir F1 y no cambiar `map2sdf` + `sdf2map`.
2. Elegir un plano de vivienda **sin muebles, con dimensiones conocidas y procedencia documentada** (preferible DXF/DWG; si es PDF/imagen, con muros rellenos y una cota para calibrar). No inventar medidas.
3. Convertir con `scripts/dxf_a_mapa.py` (o `dwg2dxf` antes; `raster_a_mapa.py` solo como plan B) → `ros2 run map2sdf map2sdf --format model` → mundo SDF; separar en el informe lo automático de lo manual.
4. Validar en Gazebo Harmonic (capturas con la región de la ventana de Gazebo, nunca `scrot -u`), medir el error **en metros** con `scripts/medir_mapa.py` y comprobar que las puertas siguen abiertas.
5. Todo dentro de `F2_PLANO_SIMPLE_GAZEBO/`, documento principal `RESUMEN F2.md` (~2 páginas) y detalle en `evidencias/DETALLE F2.md`; no avanzar a F3 sin autorización. La ruta tiene un espacio (`MAPA SOCIALTECH`): entrecomillarla siempre.
