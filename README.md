# MAPA SOCIALTECH

Plano → Gazebo Harmonic → mapa de ocupación RViz2 → mobiliario → AGV AgileX TRACER (Ubuntu 24.04, ROS 2 Jazzy, gz-sim 8.15). SOCIALTECH IQS.

| Fase | Estado | Documento |
|---|---|---|
| F0 Auditoría de repositorios | cerrada | `F0_AUDITORIA_REPOSITORIOS/RESUMEN F0.md` |
| F1 Investigación de software (DXF/DWG/PDF) | cerrada | `F1_INVESTIGACION_SOFTWARE/RESUMEN F1.md` |
| F2 Plano simple → Gazebo | cerrada | `F2_PLANO_SIMPLE_GAZEBO/RESUMEN F2.md` |
| F3 Mapa en RViz2 | cerrada | `F3_MAPA_RVIZ2/RESUMEN F3.md` |
| F4 Escenario con mobiliario | cerrada | `F4_ESCENARIO_CON_MOBILIARIO/RESUMEN F4.md` |
| F5 TRACER en el piso amueblado | **cerrada y validada en simulación, con limitaciones documentadas** (no implica equivalencia con el robot físico) | `F5_INTEGRACION_TRACER/RESUMEN F5.md` |
| F5.2 Prueba completa con el plano de la casa de José (ensayo general de todo lo restante: plano, mobiliario/máquinas, TRACER, competición, validación, entrega e instalación en GitHub) | **siguiente** | `PROMPT_COMPANERO_F5_2.md` |
| F6–F8 Plano real IQS, competición, validación | sin iniciar (carpetas vacías) | `PLAN_MAPA_SOCIALTECH.md` |

## Empezar
1. `./RESTAURAR_ENTORNO.sh` (clona repos externos, crea venv, compila LibreDWG, enlaza mallas). Lista en `REPOS_EXTERNOS.md`.
2. Demo: `F5_INTEGRACION_TRACER/scripts/demo.sh` y, en otra terminal, `F5_INTEGRACION_TRACER/scripts/teleop.sh`. Cerrar: `scripts/parar_demo.sh`.

## Para continuar (F5.2: casa de José como primera prueba real)
El relevo está en **`PROMPT_COMPANERO_F5_2.md`** (prompt listo para pegar en Claude Code). La 5.2 consiste en hacer todo lo que falta, como si fuera la entrega definitiva, pero con el plano de la casa de José; lo que funcione se repite con el plano de IQS. Incluye validar la instalación desde cero (`RESTAURAR_ENTORNO.sh` aún no se ha probado en limpio) y documentarla.

Repetir con el plano de la casa el procedimiento que luego se usará con IQS. Guía: `F5_INTEGRACION_TRACER/evidencias/ARCHIVOS PARA F6.md` (herramientas, 10 pasos, formatos, qué pedir). Los scripts de F4 tienen rutas fijas a F2/F3 que hay que cambiar al copiarlos. No inventar dimensiones: usar cotas reales.

## Avisos
- El watchdog de F5 (`scripts/watchdog_cmd_vel.py`) es solo de simulación: **no** es parada de seguridad ni fail-safe.
- Varios parámetros físicos del TRACER son estimados (ver `DETALLE F5.md`).
- Las mallas del TRACER (`tracer_ros`) no tienen licencia: no se incluyen; se enlazan desde el clon local.
- No se debe conectar el TRACER físico ni la Jetson sin autorización expresa.
- F0–F4 son de solo lectura: no modificarlas; trabajar en carpetas nuevas.
