# RESUMEN F4 — El piso de F2 amueblado con los modelos de SocialTech 2025, en Gazebo y RViz2

**Estado: F4 — CERRADA Y VALIDADA PARA EL ESCENARIO PROBADO, CON LIMITACIONES DOCUMENTADAS** (cierre autorizado por ti el 2026-11-08; no se repitieron pruebas) · F5 no iniciada, a la espera de tu autorización · **Para F5:** `evidencias/ARCHIVOS PARA F5.md` · **Anexo:** `evidencias/DETALLE F4.md`
Leyenda: ✅ medido/ejecutado · ⚠️ funciona con condiciones · 🔎 no comprobado. Rutas relativas a `F4_ESCENARIO_CON_MOBILIARIO/`. F0–F3 **no se modificaron** (ningún archivo suyo más reciente que el inicio de F4).

## 1. Conclusión
Con la metodología de 2025 (modelo del edificio + un modelo por objeto + `<include>` con pose) el piso de F2 queda amueblado con **2 mesas, 4 sillas y 2 obstáculos de prueba**. **Todo sale de un único archivo, `config/mobiliario.yaml`**: `scripts/regenerar.sh` genera el mundo Gazebo y el mapa de RViz2 sin tocar la malla del apartamento. Añadir, mover, girar y quitar una silla funciona y se comprobó (§6). Las posiciones son **de prueba**, no el mobiliario de IQS.

## 2. Modelos de SocialTech 2025 (medidos, sin modificar los originales)
| Modelo | Origen | Dimensiones medidas X×Y×Z (m) | Triángulos | Origen local original |
|---|---|---|---|---|
| mesa1 | `table1` (`mesa1.obj`) | 1,736 × 0,774 × 0,796 — **trapecio**, no rectángulo | 10 054 | **esquina** de la huella |
| mesa2 | `table2` (`mesa2.obj`) | 0,502 × 1,948 × 0,740 | 4 554 | **esquina** |
| silla | `chair` (`silla.obj`) | 0,481 × 0,523 × 0,838 | **155 001** | centro (respaldo en +Y: mira a −Y) |
| door, checkpoint | solo estudiados | puerta 0,84 × 0,135 × 2,02 (origen en la bisagra); disco r = 0,125 m, 0,1 mm | 1 808 / — | no usados |

- **Por qué en F2 parecían desplazados (explicado):** (1) las mesas tienen el origen en una esquina; (2) el `.sdf` original lleva **dos** giros de 90° (`<model><pose>` + `<visual><pose>`) y Gazebo Harmonic **sustituye** el primero por la pose del `<include>` (comprobado con `gz sdf -p`): queda un solo giro Rx(90°), que es el correcto (el OBJ es Y‑arriba). Mi script mide el desplazamiento y crea **copias** en `modelos/` con el origen en el **centro de la huella** y z = 0 en el suelo; `x, y` del YAML = centro del objeto. Los originales siguen intactos en `F0/.../models`.
- **Colisión:** mesas = malla original (probada). Silla = **cajas simples** (`silla`) en vez de la malla de 155 k triángulos (`silla_malla` se conserva para comparar): asiento y respaldo medidos de la malla; **la base de ruedas es una estimación** (la malla solo trae una huella plana). Sustitución documentada, no automática.
- Obstáculos de prueba **propios de F4** (no existen en 2025): caja 0,40 × 0,40 × 0,50 m y papelera cilíndrica r = 0,20, h = 0,60 m.

## 3. Escenario (posiciones de prueba, coordenadas del CAD en m; yaw en grados)
mesa_1 (8,90; −4,90; 0°) · mesa_2 (8,90; −6,35; 90°) · silla_N (8,90; −4,15; 0°) · silla_S (8,90; −5,65; 180°) · silla_W (7,75; −4,90; 90°) · silla_E (10,05; −4,90; −90°) · caja_1 (10,20; −6,30) · papelera_1 (7,55; −6,45).
Ningún objeto toca una pared (holgura mínima **0,18 m**, la papelera) y la más cercana a un punto de puerta es la caja (1,06 m de la «Puerta WC izq.») ✅. Mundo: `mundo/piso_amueblado.sdf` (`gz sdf -k` **Valid**; el de F2 no se sobrescribió).

## 4. Mapa para RViz2: MAPA ORIGINAL + OCUPACIÓN DEL MOBILIARIO = ACTUALIZADO
`sdf2map` (F1, sin modificar) muestrea **solo el mobiliario** (`mundo/solo_mobiliario.sdf`, sin el piso → no engorda muros) → nube de puntos → `scripts/combinar_mapas.py` la rasteriza **directamente en la rejilla del mapa de F3** por coordenadas métricas y hace la **unión** (sin restas). Banda de altura de obstáculo 0,05–1,8 m (`slice_z` en el YAML).
| Comprobación (independiente de sdf2map) | Resultado |
|---|---|
| Tamaño / resolución / origen frente a F3 | 1350×1179 / 0,01 m / (4,7299; −11,32): **idénticos** ✅ |
| Celdas de pared de F3 liberadas | **0** de 105 509 ✅ |
| Seis huecos de puerta antes → después (m) | 0,91 · 0,91 · 0,91 · 0,91 · 1,01 · 1,54 → **iguales** ✅ |
| Huella de cada objeto frente a la esperada (malla/primitivas, en metros) | IoU 0,94–0,98; error de bbox **≤ 0,01 m** ✅ |
| `/map` recibido por ROS vs PGM | 0 celdas distintas ✅ |

⚠️ Con el mapa de ocupación de `sdf2map` remuestreado, mover una silla desplazaba ±1 celda otros objetos (40 celdas, detectado por la prueba de §6); por eso se usa la nube. Ambas vías coinciden (IoU 0,998).

## 5. Gazebo ↔ RViz2 (en metros)
- Pose de cada objeto en **Gazebo en marcha** (`pose/info`) frente al YAML: error **0,000 m** y 0,0°. Huellas del `/map` frente a las esperadas con la pose de Gazebo: **≤ 0,01 m**. Medido además sobre los **píxeles que dibuja RViz2** (170 px/m, display aislado): **≤ 0,012 m** ✅ (`evidencias/logs/medicion_rviz_pixeles.json`).
- 🔎 La coincidencia con el **render** de Gazebo es cualitativa (capturas): la geometría medida es la del SDF cargado, como en F3.

## 6. Prueba de automatización (silla_W)
`scripts/prueba_mover_silla.py`: (7,75; −4,90; 90°) → (9,90; −3,30; 135°), zona libre (0,83 m de pared). Resultado ✅: Gazebo carga el mundo regenerado con la silla en (9,90; −3,30; 135°) (error 0); en el mapa nuevo la huella nueva está ocupada al 98,6 % (0 % antes); las 1 961 celdas del núcleo de la huella antigua pasan de ocupadas a **libres**; **0** celdas cambiadas fuera de las dos huellas, **0** paredes liberadas, 6 puertas iguales. Se restauró el YAML (idéntico). Ciclo añadir → mover → quitar: mundo y mapa vuelven **byte a byte** al original (MD5).
Comandos: `scripts/mobiliario.py anadir|mover|quitar|listar …` (o editar el YAML) y `scripts/regenerar.sh`.

## 7. Colisiones (sin robot) ✅
Bolas dinámicas de 5 cm soltadas sobre cada objeto (`scripts/prueba_colisiones.py`): se detienen a la altura esperada en mesa_1 (0,846 m), caja (0,55), papelera (0,65), suelo (0,05); en mesa_2 queda **9,5 mm más baja** de lo esperado (0,780 vs 0,790, sin explicar); asiento: 0,480 m con la colisión simple frente a 0,466 m con la malla (**+1,4 cm**). Bola lanzada contra la caja: para en la cara (x = 10,45); contra la pared: no la atraviesa. ⚠️ Con la malla original, una bola a ras de suelo **atraviesa** la base de la silla (la malla es porosa); la base estimada de 4 cm la **sobrepasa rodando** (bola de 10 cm): no hay prueba lateral válida de la base de la silla.

## 8. Rendimiento (Gazebo Harmonic, 500 it. headless ×3; GUI 30 s)
| | F2 sin muebles | F4 silla simple | F4 silla malla |
|---|---|---|---|
| Tiempo total de carga + 500 it. | 2,63–2,66 s | 2,67–2,68 s | 3,41–3,45 s |
| RAM servidor (máx.) | 147 MB | 174 MB | 405 MB |
| GUI: RAM / CPU media | 391 MB / 121 % | 524 MB / 137 % | no medido |
| Factor de tiempo real | 0,999 | 0,999 | — |
La malla de 155 k triángulos como colisión cuesta +0,8 s y +230 MB; la colisión simple lo evita. 0 errores/avisos de Gazebo (solo `libEGL warning` del driver). RViz2: 192 MB, 3 % CPU, `map_server` 49 MB; el único error es el GLSL ya conocido de F3.

## 9. Demostración
```bash
cd "/home/jose-angel/Desktop/MAPA SOCIALTECH/F4_ESCENARIO_CON_MOBILIARIO"
scripts/regenerar.sh     # tras editar config/mobiliario.yaml
scripts/demo.sh          # Gazebo amueblado + map_server + TF + RViz2; Ctrl+C o scripts/parar_demo.sh cierra todo
```
Iniciada y cerrada **3 veces** desde cero: `map_server` activo en ~1,9 s, Gazebo listo en ~4 s, `/map` idéntico al PGM, **0 procesos residuales** (cierre por grupo de procesos, sin `pkill`).

## 10. Limitaciones y avisos
- Posiciones de prueba; no son el mobiliario ni las medidas de IQS. `door` y `checkpoint` solo estudiados.
- Base de la silla estimada; sillas negras (el `.mtl` original tiene Kd = 0; no lo comparé con 2025). Altura de banda del mapa (0,05–1,8 m): depende de dónde esté el lidar del Tracer → **decidir en F5**.
- ⚠️ **Incidencia de capturas:** dos capturas con `ffmpeg` sobre tu pantalla incluyeron un aviso de escritorio y, la segunda, **una ventana de tu navegador**. Las **borré al instante** (no quedan copias) y lo cambié: las mediciones de RViz usan un display aislado (Xephyr :5) y las de Gazebo se recortan sin barra de título. Tu escritorio no se vuelve a capturar.
- `gz /gui/screenshot` devuelve «true» pero no escribe archivo (no investigado).

## 11. Cierre (2026-11-08)
Aprobado por ti: 2 mesas, 4 sillas, caja y papelera; modelos de SocialTech 2025; configuración editable `mobiliario.yaml`; mundo SDF y mapa generados automáticamente; 105 509 celdas de pared conservadas; seis puertas conservadas; Gazebo–RViz2 con desviaciones de hasta 0,012 m; prueba de añadir/mover/eliminar; demo reproducible (3 ejecuciones); rendimiento mediante colisiones simplificadas.
**Limitaciones que se mantienen (cierre):**
1. Colisión lateral de la silla no completamente validada (la bola sobrepasa la base de 4 cm; con la malla original la atraviesa).
2. Dimensiones de la base de ruedas **estimadas** (cilindro r 0,25 m, h 0,04 m).
3. Diferencia de 9,5 mm en la colisión de mesa_2 (sin explicar).
4. Banda de alturas del mapa (0,05–1,8 m) pendiente de revisar con el lidar del Tracer (F5).
5. Correspondencia con el render de Gazebo comprobada solo cualitativamente.
Nada eliminado; F0–F3 sin modificar. **Evidencias:** `evidencias/capturas_gazebo/` (02 cenital, 03 oblicua), `capturas_rviz/` (01 completa, 02 zoom medido), `figuras/mapas_base_actualizado_movimiento.png`, `logs/*.json`.
