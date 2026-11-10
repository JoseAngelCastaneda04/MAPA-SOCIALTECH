# RESUMEN F5.2 — Percepción y localización del TRACER en la casa de José (estado: EN CURSO, pendiente de tu prueba conduciendo)

Todo es **simulación**. No se modificó F0–F5 (solo se leen), no se instaló nada, no hay commit ni push. Rutas relativas a `F5_2_CASA_JOSE/`.

## 1. Cómo ejecutarlo
```bash
cd "/home/jose-angel/Desktop/MAPA SOCIALTECH/F5_2_CASA_JOSE"
scripts/demo_f52.sh                      # Gazebo (mundo *_gt) + puente + AMCL + monitor + RViz2
../F5_INTEGRACION_TRACER/scripts/teleop.sh   # en OTRA terminal: i , j l (mantén la tecla), k parar
scripts/parar_f52.sh                     # cierra todo (por grupos de proceso)
F52_ERR_X=0.3 F52_ERR_Y=-0.2 F52_ERR_YAW_DEG=10 scripts/demo_f52.sh   # pose inicial de AMCL equivocada a propósito
```
RViz2: **verde** = posición REAL (Gazebo) · **amarillo** = SOLO odometría · **cian** = estimación AMCL · **magenta** = LiDAR (obstáculos detectados) sobre el mapa gris/negro de ocupación · **rojo** = zonas prohibidas (solo visuales) · nubes de partículas de AMCL · TF. Texto sobre el robot con el error de odometría y de AMCL. «2D Pose Estimate» fija la pose inicial.

## 2. Diagnóstico (hechos)
- **F5 NO tenía localización real**: `map→odom` era un `static_transform_publisher` con la pose inicial; `odom→base_footprint` lo da el DiffDrive de Gazebo. Es decir, «dónde está el robot» = odometría pura.
- **F5.2**: se elimina ese TF estático (en el lanzador nuevo; F5 intacto) y **`map→odom` lo publica solo `nav2_amcl`**. Auditoría de 8 s: `map→odom` 80 msg (solo AMCL), `odom→base_footprint` (Gazebo), resto de robot (rsp); **0 hijos con varios padres**; `map→odom` no está en `/tf_static`.
- **Dependencias**: ya instaladas `nav2_amcl`, `nav2_map_server`, `nav2_costmap_2d`, `nav2_rviz_plugins`, `robot_localization`, `teleop_twist_keyboard`. No se instaló nada.
- **Verdad de terreno**: `OdometryPublisher` del mundo `piso_amueblado_tracer_gt.sdf` (ya existía en F5) → `/gz/odom_gt`. Solo la lee el monitor; **no entra en TF** (no contamina a AMCL). Mundo = mapa, sin desplazamiento.

## 3. Medidas (CSV en `logs/sesion_prueba_recorrido_empuje_reloc.csv`; tiempos de simulación)
| Prueba | Odometría sola | AMCL |
|---|---|---|
| Recorrido libre «S» de 9,2 m (0,2 m/s, 0,5 rad/s), 77 s | posición media **1,7 mm**, máx 3,4 mm; yaw máx 0,11° | posición media **25 mm**, máx 49 mm; yaw media 0,56°, máx 1,9° |
| Empuje de 15 s contra la pared (ruedas patinan; real avanzó 0,45 m) | **deriva 2,53 m**, 8,5° (coincide con los 2,54 m de F5) | **no la corrige**: error final 2,24 m (la estimación sigue a la odometría y acaba dentro/detrás de la pared) |
| Tras `/reinitialize_global_localization` + 3 ciclos de giros y pequeños avances (~80 s) | sigue con ~2,5 m de error | **vuelve a 3,6 cm** y 0,8° |
- **Conclusión honesta:** con odometría **sin ruido y sin patinaje** (caso de la simulación) la odometría es *mejor* que AMCL (AMCL añade ~2,5 cm de ruido propio). AMCL **no corrige** una deriva grande y repentina por sí solo en modo seguimiento; **sí se recupera** con relocalización global y movimiento. Solo se probó **un** escenario por tipo (no estadística). La odometría real del TRACER tendrá ruido/patinaje que aquí no existe.
- **LiDAR vs mapa** (`scripts/comprobar_lidar.py`, trazado de rayos desde la pose real, sensor a 0,2125 m delante del centro): mediana **7–9 mm**, 72–78 % de los haces a < 5 cm; **22–26 % ven más lejos que el mapa** (sillas/tableros que el LiDAR a 0,20 m no ve; limitación ya documentada en F5). Tras girar 114° cambian el **96 %** de los haces. *(Un primer cálculo mío salió con 23 cm de error porque ignoré el desplazamiento del sensor; corregido.)*
- RViz2 carga `rviz/f52.rviz` sin errores de clase (solo el GLSL inocuo conocido). **No he capturado tu pantalla**: la comprobación visual la haces tú.

## 4. Diferencias entre las tres posiciones
- **Real (Gazebo)**: la única verdad; en el robot físico no existe (hace falta un sistema externo).
- **Odometría**: integra las ruedas; precisa a corto plazo, **deriva sin límite** si hay patinaje o choque.
- **Localización (AMCL)**: compara LiDAR con el mapa; no deriva con el tiempo si el mapa es fiel, pero es más ruidosa (cm) y **solo corrige si el error inicial es pequeño o se relocaliza**; depende de que el mapa coincida con lo que ve el LiDAR (sillas: no).

## 5. Tarea 4 — Navegación (solo estudio; NO implementada)
- **No existe ningún costmap** en el proyecto ni nodo `nav2_costmap_2d` en marcha.
- **Zonas prohibidas: no existían en F0–F5** (búsqueda en todo el proyecto). Las rojas de F5.2 son un **ejemplo** (`config/zonas_prohibidas.yaml`, `EJEMPLO_zona_1`) para probar el mecanismo; **dime las reales**. Siguen siendo solo visuales.
- Camino propuesto (a aprobar): `nav2_costmap_2d` con `StaticLayer` (mapa) + `ObstacleLayer` (`/scan`) + `InflationLayer`, y las zonas como **KeepoutFilter** (máscara PGM + `costmap_filter_info_server`, ya instalado). Limitaciones: el LiDAR 2D a 0,20 m no ve sillas ni tableros (hay que añadirlos por mapa o usar otro sensor); AMCL debe estar bien localizado (si no, el plan atraviesa paredes); el watchdog no es seguridad; sin parada de emergencia certificada; a velocidades > 0,5 m/s no hay validación.
- **Narcís** usa `nav2_costmap_2d` con `ObstacleLayer`+`StaticLayer`+`DecayObstacleLayer` propia, `SmacPlanner2D`, `RegulatedPurePursuit` y localización **gn_loc** (scan-to-map) con **LiDAR 3D Livox + FAST-LIO2**, no AMCL 2D: lo que probamos aquí **no es su localizador**.

## 6. Pendiente / decisiones tuyas
1. Tu prueba conduciendo con RViz2 (comandos arriba).
2. Definir las zonas prohibidas reales.
3. ¿Afinar AMCL (`recovery_alpha_*`, más `z_rand`) para que se relocalice solo? Es un cambio de configuración propia de F5.2; no lo he hecho.
4. ¿Autorizas diseñar la navegación (Tarea 4)? No implementada.
5. Memoria/anexos: no he creado `evidencias/DETALLE F5.2.md` (esta síntesis cubre lo medido).
