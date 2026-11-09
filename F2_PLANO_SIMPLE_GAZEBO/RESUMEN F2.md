# RESUMEN F2 — Un plano externo (no dibujado por nosotros) convertido a Gazebo Harmonic

**Estado:** ✅ **F2 cerrada y validada para el caso probado** (cierre autorizado por ti el 2026-11-08) · F3 **no** iniciada, a la espera de tu autorización · **Anexo:** `evidencias/DETALLE F2.md` (§J = cierre) · **Para F3:** `evidencias/ARCHIVOS PARA F3.md`
Leyenda: ✅ verificado con prueba · ⚠️ funciona con condiciones · ❌ no funciona · 🔎 no comprobado

## 1. Conclusión

Un DWG de AutoCAD 2018 **descargado de Internet** (no dibujado por nosotros) se convirtió con la cadena de F1 a un **mapa de ocupación a escala, un modelo 3D de muros y un mundo SDF válido** que carga en Gazebo Harmonic. Los huecos de puerta quedaron abiertos y las dimensiones medidas coinciden con las cotas del plano (≤ 0,02 m en las 6 cotas comprobadas; ver §8 para el error real frente a la geometría). **No funcionó sin intervención**: hubo 5 correcciones (§4). Esto prueba la cadena con **un** plano; no que valga para cualquier plano.

## 2. El plano

| | |
|---|---|
| Fuente | DesignsCAD, [«Apartment unit floor plan with dimensions and wet areas»](https://designscad.com/downloads/apartment-unit-floor-plan-with-dimensions-and-wet-areas/) (subido por «Blueprint Hub», 2026-06-03). La web lo describe como planta de una unidad de la torre B, en portugués, unidades métricas |
| Descarga | 2026-11-07, botón «Free Download» pulsado por ti (verificación anti-bot manual). ZIP SHA-256 `82766fb7…63ef7f86`; DWG SHA-256 `b22a1c95…533339a1` (AutoCAD 2018, `AC1032`, 6 497 351 B) |
| Licencia | [Términos del sitio](https://designscad.com/terms-conditions/): *«Downloaded files may be used for your own personal, educational, or commercial projects. You may not redistribute, resell, or sublicense the files as standalone products.»* Es licencia del **sitio**; no hay licencia propia del autor. **El original no se publica**; queda solo en `original/` |
| Contenido | Un piso: 3 dormitorios, 2 aseos, salón abierto y zona técnica, con cotas y 6 puertas. **No es vivienda pública** (pedías pública; no la encontramos con PDF+DWG y licencia clara) |
| Archivo | 34 026 entidades, 27 capas, 41 declaradas. Dibujo con detalles de baños y climatización repartidos en ~100 m de extensión; el piso ocupa 13,1 × 11,4 m |

## 3. Cadena ejecutada y quién hace cada paso

| Paso | Herramienta | Auto / manual |
|---|---|---|
| DWG → DXF | LibreDWG 0.14 `dwg2dxf` (0,7 s; avisos «Unstable Class» en cotas asociativas y render, sin efecto) | Automático ✅ |
| Aislar el piso del resto del dibujo | `ezdxf` (`scripts/recortar_piso.py`) | **Manual**: elegir la ventana y las capas |
| Unidades | `dxf_a_mapa.py --unidades 6` | **Manual**: el archivo declara milímetros pero está dibujado en metros |
| Muros como líneas sueltas → lazos cerrados | `ezdxf.edgeminer` (`scripts/cerrar_lazos.py`, tolerancia 1 mm) | **Manual**: elegir capas; solo cierra lo que el CAD ya cierra |
| DXF → mapa nav2 (0,02 m/celda) | `dxf_a_mapa.py` (F1, sin cambios) | Automático ✅ |
| Mapa → modelo 3D | `map2sdf --format model --wall-height 2.5` (F1, sin cambios) | Automático ✅ (altura = parámetro, no dato del plano) |
| Mundo SDF | `<include>` del modelo + suelo + luz (estructura de ICAI_A501 y de F1) | Manual (plantilla) |
| Comprobar | `gz sdf -k`, `gz sim`, GUI con capturas, `scripts/medir_cotas.py` | Automático ✅ |
| **PDF derivado** | LibreCAD `dxf2pdf` (1:50, A3) → `pdftoppm` → `raster_a_mapa.py --rellenar` | ⚠️ Ver §5 |

## 4. Problemas encontrados y correcciones

1. **Unidades erróneas:** `INSUNITS=4` (mm) pero geometría en metros (cotas 2,50 / 4,00 y arcos de puerta de 0,81 lo prueban). Sin corregir, el piso mide **1 × 1 píxel (1,8 cm)**. Se fuerza `--unidades 6`.
2. **Piso mezclado con detalles externos** (lavabos y climatización dibujados fuera del piso): sin recorte, al añadir las capas de mampostería el mapa pasó a 33 × 95 m. Recorte con `ezdxf` y lista de entidades descartadas.
3. **Muros como líneas sueltas** (capas `ALVENARIA_*`): el script de F1 las ignora. `edgeminer` halla los lazos que el CAD ya cierra: 11 + 5. Aporta lo que faltaba (frente del dormitorio 1 de 1,55 × 0,14 m, tabique de 0,14 × 0,70 m, cuadrado de 0,62 m).
4. **`map2sdf` rellena el interior a 0,05 m/celda** (tapa STL de 149 m² frente a 11,4 m² de muro). Es un fallo de triangulación que depende de la resolución: falla a 0,025, 0,04 y 0,05; funciona a **0,02** (tapa 11,48 m², IoU con el mapa 0,9955). Se usa **0,02 m/celda** como mapa maestro. No se modificó `map2sdf` (causa raíz sin analizar).
5. **Mis propios errores de captura:** la primera captura incluyó otras ventanas tuyas (posición mal calculada con `xdotool`). **La borré al instante.** Ahora `scripts/captura_ventana.sh` usa `xwininfo` y exige que la ventana de mi PID sea la activa. Además, dije que el PID 3406 era otro Gazebo tuyo: era `mutter-x11-frames` (el gestor de ventanas); no hubo otra sesión.

## 5. Resultados medidos (error en metros contra las cotas del plano)

| Cota (CAD) | Ruta DXF (mapa 2 cm) | Ruta PDF derivado |
|---|---|---|
| Dormitorios: ancho 2,50 / 2,50 / 2,90 m | 0,000 / 0,000 / 0,000 | +0,02 / 0,000 / +0,02 |
| Fondo dormitorios 4,00 / 4,00 m; lado E 5,75 m | 0,000 / 0,000 / +0,010 | +0,02 / +0,02 / +0,01 |
| Huecos de puerta (6 de 6 libres): 4 de 0,90, dormitorio 3 de 1,00, entrada de 1,54 m (CAD a 1 cm: 0,90 / 1,00 / 1,53) | iguales al CAD ✅ | ±0,02 ✅ |
| Entorno 3D (STL) vs CAD | 13,10 × 11,40 × 2,50 m vs 13,09 × 11,39 (altura = parámetro) | — |
| IoU frente al mapa DXF | — | 0,92 (diferencias de 1 celda en bordes) |

- **Gazebo Harmonic:** `gz sdf -k` → **Valid.**; `gz sim` 500 iteraciones **sin errores ni avisos**; GUI con 4 capturas en `evidencias/capturas_gazebo/` (cenital con norte arriba, oblicua, entrada oeste, picado de aseos). Orientación y distribución coinciden con el CAD (`evidencias/figuras/comparacion_cad_mapa_gazebo.png`).
- **PDF derivado** (`derivados/pdf_derivado/`, **generado desde el DWG, no es un PDF independiente**): salió monocromo con muros como contorno (el caso que F1 marcaba como ❌) y aun así funcionó **porque se filtraron antes las capas de muros** y los bloques eran contornos cerrados. Pierde el origen CAD; para comparar alineé por la esquina de la tinta (4,93; −11,12). ⚠️ Condicionado a ese filtrado.

## 6. Lo que NO se reconstruye o no se verificó

- **Baranda de la zona técnica** (mureta 0,80 m + reja, 1,10 m): el CAD solo trae una línea sin grosor; **queda abierta** (≈2,2 m).
- **Hoja corredera** (~1,9 m, capa PORTAS, sin arco): hueco libre. 🔎 No sé si es puerta o ventana fija.
- **Ventanas:** quedan dentro del muro (cerradas); alféizares y alturas no existen en el plano. **Altura de muro 2,5 m: parámetro.**
- **El piso no es estanco:** la entrada oeste (≈1,5 m) y la zona técnica dan al exterior; no hay pasillo de acceso.
- Sin hojas de puerta, mobiliario, sanitarios ni suelo propio (el suelo es un plano). Las 7 polilíneas abiertas de 1 cm no se usan.
- **Cotas verificadas: solo 6 (dormitorios).** Salón, aseos y zona técnica no tienen medición contra cota.
- No se ha visto en RViz2 (F3). Las capturas son cualitativas; las medidas salen del mapa y del STL.

## 7. Decisiones tuyas (2026-11-08) y cómo se aplicaron

1. **Precisión:** sin tolerancia amplia; errores reales en metros. → Medidos contra una verdad geométrica a 2,5 mm (§8).
2. **Baranda y zona técnica:** sin muro ficticio. → **No reconstruida**; queda abierta como en el plano. **Revisar al integrar el Tracer (F5)**.
3. **Plano:** el piso de DesignsCAD es el primer caso externo; no se busca más. Original conservado en `original/`, sin redistribuir.
4. **Fallo de `map2sdf`:** documentado con evidencias (§4, `DETALLE` §F). **No está resuelta la causa**; solo hay una configuración que funciona para este caso.

## 8. Cierre: versión final y errores medidos

**Comprobaciones de la versión a 0,02 m/celda (repetidas hoy):** tapa del STL 11,478 m² frente a 11,454 m² de muro (**sin relleno**); `gz sdf -k` del modelo y del mundo *Valid.*; 500 iteraciones de `gz sim` con 0 errores/avisos; las 6 puertas libres. ✅

| | Mapa 0,02 m (pedido) | Mapa 0,01 m (añadido) |
|---|---|---|
| Área de muro (verdad CAD a 2,5 mm: **10,534 m²**) | 11,454 (**+8,7 %**) | 10,551 (+0,16 %) |
| IoU con la geometría del CAD | 0,917 | 0,998 |
| Desviación máxima de borde | 0,015 m | 0,0075 m |
| Tapa del STL / caja | 11,478 m² / 13,10 × 11,40 | 10,558 m² / 13,09 × 11,39 |
| 6 cotas de dormitorio frente a la **geometría** del CAD | −0,01 m en 5, 0,00 en 1 | 0,00 en las 6 |
| Huecos 4 aseos/dorm. · dorm. 3 · entrada (CAD: 0,91 · 1,01 · 1,54) | 0,90 · 1,00 · 1,54 | 0,91 · 1,01 · 1,54 |
| `gz sdf -k` / `gz sim` 500 it. / relleno de `map2sdf` | Valid / 0 errores / no | Valid / 0 errores / no |

- **Corrección a lo que te dije antes:** el CAD mide **+0,01 m más que la cota escrita** (p. ej. 2,51 frente a 2,50), y no es un artefacto de medida. El «0,000» del mapa de 2 cm era cuantización (el engorde de muros se lleva 1 cm), no más fidelidad. Con 2 cm los muros salen ≈ 0,5 cm más gruesos por cara y los huecos ≈ 1 cm más estrechos.
- **Resolución:** el mapa de 0,02 m es el que pediste y pasa las pruebas, pero **no es el más preciso**. Con tu criterio de máxima precisión añadí la versión 0,01 m (`mapa/piso_1cm.*`, `mundo/piso_designscad_1cm.sdf`), que también supera las pruebas (captura `06_cenital_1cm.png`). **No sustituí nada**; ambas existen. **Que 0,01 funcione no prueba que la causa del fallo esté entendida.**
- **Herramientas:** LibreDWG 0.14, ezdxf 1.4.5, OpenCV 5.0.0, Python 3.12.3, LibreCAD CLI, poppler 24.02.0, `map2sdf`/`sdf2map` (F1, sin modificar), Gazebo Sim 8.15.0, gz-sdformat 14.9.0, ROS 2 Jazzy.
- **Intervenciones manuales:** las 5 del §4, más elegir la resolución y comprobar el STL.
- **Capturas:** `evidencias/capturas_gazebo/` 01, 02, 03, 05 (0,02) y 06 (0,01), solo la ventana de Gazebo.
- **Nada eliminado:** mapas de 5 cm, referencia de 1 cm, registros y capturas anteriores siguen en su sitio. F0 y F1 no se tocaron.

## 9. Pendiente de tu decisión

- ¿Qué mapa usa F3: **0,02 m** (pedido) o **0,01 m** (más fiel)? Por defecto, F3 partirá del de 0,02 m salvo que digas otra cosa.
- **Autorización para empezar F3.** No la he asumido; no hay archivos nuevos en `F3_MAPA_RVIZ2/`.

**Evidencias (`evidencias/`):** `DETALLE F2.md`, `capturas_gazebo/`, `figuras/`, `logs/`, `cotas_verificadas.json`. Archivos: `original/` (DWG y ZIP sin modificar), `derivados/`, `mapa/`, `mundo/`, `scripts/`.
