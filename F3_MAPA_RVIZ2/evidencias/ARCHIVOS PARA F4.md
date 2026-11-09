# Archivos y componentes de F3 (y F2) que F4 puede reutilizar
F4 **no se ha iniciado**. Rutas relativas a `F3_MAPA_RVIZ2/`; `F2/` = `../F2_PLANO_SIMPLE_GAZEBO` (solo lectura).

| Para qué | Archivo | Notas |
|---|---|---|
| Demo completa | `scripts/demo.sh`, `demo_gazebo.sh`, `parar_demo.sh` | `demo_gazebo.sh` tiene fijado el mundo de F2; en F4 habrá que apuntarlo al mundo nuevo (copiar, no editar F2) |
| Publicar mapa + RViz2 | `launch/mapa_rviz.launch.py` (argumento `mapa:=`), `config/piso_1cm.rviz` | Para un mapa nuevo basta otro YAML en `mapa/`; la config RViz es genérica (frame `map`, Map con Transient Local, vista cenital) |
| Mapa/mundo base | `mapa/piso_1cm.*`, `F2/mundo/piso_designscad_1cm.sdf`, `F2/mundo/modelos/` | Estructura: modelo de muros + mundo con `<include>`; necesita `GZ_SIM_RESOURCE_PATH` y `SDF_PATH` |
| Comparar mapa ↔ CAD/STL | `scripts/volcar_mapa_topic.py`, `comparar_geometria.py` | `comparar_geometria.py` compara muros; habría que ampliarlo para mobiliario (hoy solo lee las capas de muro) |
| Medir en píxeles de RViz2 | `scripts/medir_rviz.py` | Genérico en vista; los puntos de puerta salen de `cotas_verificadas.json` |
| Rendimiento | `scripts/rendimiento.sh` | Tiempo de carga, RAM, CPU, 20 ciclos lifecycle |
| Capturas sin otras ventanas | `scripts/captura_ventana.sh` (RViz2), `F2/scripts/captura_ventana.sh` (Gazebo) | Por PID y comprobando foco; nunca `scrot -u` |
| sdf2map / map2sdf | `F1/ws/install` | Sin modificar; `map2sdf` falla con la tapa a 0,025–0,05 m (F2 §4); usar 0,01–0,02 m |

## Lecciones que afectan a F4
- `OccupancyGrid.data` empieza por y mínima; el PGM, por y máxima: voltear al comparar.
- TF: hoy solo `map→world` identidad; revisar en F5.
- Tras cualquier mapa nuevo comprobar `lifecycle get` = `active`, el QoS Transient Local y que el origen del YAML = pose del modelo.
- No usar `pkill -f` con patrones que aparezcan en tu propia línea de comandos; `parar_demo.sh` cierra por grupo de procesos.
- Pendientes heredados: RAM del servidor tras ciclos (observación), error GLSL (sin impacto observado), baranda/hoja corredera/ventanas sin reconstruir.
