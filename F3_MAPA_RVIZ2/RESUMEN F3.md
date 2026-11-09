# RESUMEN F3 — El mismo piso en Gazebo (3D) y RViz2 (mapa de ocupación)

**Estado:** ✅ **F3 CERRADA Y VALIDADA para el escenario probado** (cierre autorizado por ti el 2026-11-08) · F4 **no** iniciada, a la espera de tu autorización · **Para F4:** `evidencias/ARCHIVOS PARA F4.md` · **Anexo:** `evidencias/DETALLE F3.md`
Leyenda: ✅ medido/ejecutado · ⚠️ funciona con condiciones · 🔎 no comprobado

## 1. Conclusión
Con el mapa de **0,01 m/celda** (`mapa/piso_1cm.*`, copia idéntica por SHA al de F2), `nav2_map_server` lo publica en `/map`, RViz2 lo dibuja y **coincide con el CAD y con el modelo que carga Gazebo** (errores en metros en §3). Las 6 puertas están abiertas en los tres. La demostración arranca y se cierra con 2 scripts y se repitió desde cero (§6). Hay dos limitaciones sin resolver (§5): el error GLSL de RViz2 (no afecta a lo medido) y que la comparación con Gazebo es del **modelo cargado**, no de píxeles de su render en perspectiva.

## 2. Avisos investigados
| Aviso | Causa (comprobada) | ¿Afecta? | Acción |
|---|---|---|---|
| **Global Status naranja** | `Fixed Frame: No tf data`: nadie publica el frame `map` | Solo estético; el mapa se dibujaba igual | ✅ TF estático **identidad** `map→world` (los dos usan coordenadas del CAD). Pasa a **Ok** y desaparece |
| **Error GLSL** `indexed_8bit_image.vert` («samplers de distinto tipo en la misma unidad de textura») | Shader de la paleta del display *Map* al enlazarse en **Mesa/Intel** (RViz2 no usa la NVIDIA). **No es la causa del aviso anterior**: con el TF arreglado el error sigue en el log | Geometría: **no** (medida sobre los píxeles dibujados, ±1 píxel); color: libre = 255, ocupado = 0; rendimiento: no apreciable (§4) | Documentado, sin cambios en drivers ni configuración global |

## 3. Comparación numérica (referencia: DXF de F2 en metros)
| Magnitud | CAD | Mapa `/map` (RViz2) | STL en Gazebo | Error |
|---|---|---|---|---|
| Caja de muros (m) | 13,09 × 11,39 | 13,09 × 11,39 | 13,09 × 11,39 | **0,000** |
| Esquina inf. izq. / sup. der. (m) | (4,93; −11,12) / (18,02; 0,27) | igual | igual | 0,000 |
| Origen / pose del modelo | — | (4,7299; −11,32) | (4,7299; −11,32), también en **Gazebo en marcha** | 0 |
| Márgenes libres del mapa (no son error) | — | 0,20 · 0,20 · 0,21 · 0,20 | — | — |
| Área de muro (m²) | 10,534 | 10,551 | 10,559 | +0,017 / +0,025 |
| IoU a 2,5 mm | — | 0,9982 | 0,9975 (0,9992 vs mapa) | — |
| Desviación de borde (máx.) | — | 0,0075 m | 0,009 m | ≤ 1 celda |
| Orientación (IoU del mapa con espejo V / espejo H / 180°) | — | 0,05 / 0,10 / 0,03 (correcta: 0,998) | — | sin giros ni espejos |
| Habitaciones (núcleos libres) | 7 | 7 | 7 | centros ≤ 0,001 m |

- **Transformación `map`↔`world`:** ninguna salvo la identidad. El origen del mapa ya va en el YAML. No se aplicó ningún desplazamiento.
- **Puertas** (hueco libre medido cortando a lo largo del eje, en m): ancho 0,91 · 0,91 · 0,91 · 0,91 · 1,01 · 1,54 en CAD, mapa y STL (a 0,05, 1,25 y 2,45 m de altura: igual). Extremos del hueco: error ≤ 0,0024 m (entrada, lado del mapa); el resto ≤ 0,0001 m. **Medidos también sobre los píxeles de RViz2** (zoom 300 px/m, ±0,003 m): 0,91 · 0,91 · 0,91 · 0,91 · 1,01 · 1,54 ✅.
- Las 6 cotas de dormitorio: 2,51 / 2,51 / 2,91 / 4,01 / 4,01 / 5,76 m, igual en los tres (error 0,000).

## 4. Rendimiento (0,01 m; comparado con 0,02 m)
| | 0,01 m | 0,02 m |
|---|---|---|
| Carga del PGM (marcas de tiempo del nodo) | **22 ms** | 7 ms |
| RAM `map_server` (activo) | 48 MB | 44 MB |
| RAM RViz2 | 195 MB | 194 MB |
| CPU RViz2 media | 5,2 % (180 s) | 5,6 % (60 s) |
| Fluidez | 31 fps (barra de RViz2) | 31 fps |
| Suscriptor tardío (transient local) | 0,18 s | 0,16 s |
| 20 ciclos deactivate/cleanup/configure/activate | sin fallos; RAM 48→73 MB | sin fallos; 43→51 MB |

0 errores y 0 avisos de RViz2 salvo el GLSL. **0,01 m sigue siendo adecuado** como principal. ⚠️ La RAM del servidor crece tras reciclar 20 veces; no sé si es fuga o caché del asignador (no se probó más tiempo).

## 5. Limitaciones
- 🔎 La comparación con Gazebo usa el STL y la pose del modelo cargados (y `pose/info` en ejecución), **no** mide el render de Gazebo (perspectiva). Las capturas son cualitativas. El STL sale del mismo mapa (`map2sdf`), por lo que su parecido con el mapa no es independiente; el CAD sí lo es.
- 🔎 Salón, aseos y zona técnica: sin cotas escritas que contrastar (límite heredado de F2). Baranda abierta, hoja corredera, ventanas: no evaluadas.
- 🔎 Probado solo con el color «map» de RViz2 y en esta máquina (Mesa/Intel). No probé la NVIDIA.
- En el 2.º arranque la captura de Gazebo falló (PID equivocado en mi comando); el 2.º arranque se verificó por `pose/info`, `/map` idéntico y captura de RViz2.

## 6. Demostración (desde cero, sin procesos previos)
```bash
cd "/home/jose-angel/Desktop/MAPA SOCIALTECH/F3_MAPA_RVIZ2"
scripts/demo.sh            # Gazebo (mundo 1 cm de F2, solo lectura) + map_server + TF + RViz2; Ctrl+C lo cierra todo
scripts/parar_demo.sh      # alternativa desde otra terminal (por PID, sin pkill por nombre)
scripts/demo.sh piso_2cm   # opcional: mapa de 2 cm
```
Verificado **2 veces** (arranque → comprobación → cierre → arranque): `map_server` active, `/map` idéntico, modelo `piso` en (4,7299; −11,32), Global Status Ok, cierre sin restos.

## 7. Evidencias
`evidencias/capturas_gazebo/` (02 cenital, 03 oblicua 3D), `evidencias/capturas_rviz/` (04 demo, `medicion/` con 7 vistas medidas), `evidencias/figuras/comparacion_geometria_diferencias.png` (gris = coincide; sin zonas rojas/azules apreciables), `evidencias/logs/`. Archivos nuevos: `mapa/`, `config/piso_1cm.rviz`, `launch/`, `scripts/`. F0, F1 y F2 **no se modificaron**.

## 8. Cierre y decisiones tuyas (2026-11-08)
1. **Resolución principal: 0,01 m/celda** para este apartamento (0,02 m queda como alternativa: `scripts/demo.sh piso_2cm`).
2. **Error GLSL y NVIDIA:** no se investigan más; ambos quedan documentados (§2, DETALLE §C) **sin impacto funcional observado** en las pruebas.
3. **Memoria del servidor tras 20 ciclos de lifecycle (48→73 MB a 1 cm; 43→51 MB a 2 cm):** **observación pendiente**, no se afirma que haya fuga; no se hizo prueba prolongada.
4. **TF estático identidad `map→world`:** válido para la demo actual. **Revisar la estructura TF al integrar el Tracer (F5).**
5. **Demostración conservada:** `cd "/home/jose-angel/Desktop/MAPA SOCIALTECH/F3_MAPA_RVIZ2" && scripts/demo.sh` (§6).
6. Nada eliminado; F0, F1 y F2 sin modificar. **F4 (mobiliario con la estructura de ICAI_A501, objetos → mapa con `sdf2map`) no se ha comenzado ni requiere hoy ningún cambio en F3.**
