# Archivos de F2 que F3 reutilizará (RViz2 del mismo apartamento)

F3 **no se ha empezado** y `F3_MAPA_RVIZ2/` está vacía. Rutas relativas a `F2_PLANO_SIMPLE_GAZEBO/`.

| Para qué | Archivo |
|---|---|
| Mapa nav2 (0,02 m/celda, versión pedida) | `mapa/piso.pgm` + `mapa/piso.yaml` (resolución 0,02; origen [4,7299; −11,32; 0]; 675 × 590; `negate: 0`, `occupied_thresh 0,65`, `free_thresh 0,196`) |
| Mapa de alta precisión (0,01) | `mapa/piso_1cm.pgm` + `mapa/piso_1cm.yaml` (1350 × 1179; mismo origen) |
| Mundo de Gazebo (comparar con RViz2) | `mundo/piso_designscad.sdf` (+ `mundo/piso_designscad_1cm.sdf`), modelos en `mundo/modelos/` (hace falta `GZ_SIM_RESOURCE_PATH` y `SDF_PATH` apuntando ahí) |
| Verdad geométrica para comparar | `derivados/plano_piso_muros.dxf` (en metros) y `evidencias/cotas_verificadas.json` (puntos, ejes y cotas) |
| Medir mapas | `scripts/medir_cotas.py <mapa.yaml> <cotas.json> [salida.json]`; F1: `medir_mapa.py` |
| Capturas de referencia | `evidencias/capturas_gazebo/01_cenital_norte_arriba.png` (norte arriba) y `06_cenital_1cm.png` |
| Herramientas F1 sin modificar | `ws/install` (`sdf2map`, `map2sdf`), `herramientas/venv` (ezdxf, OpenCV) |

## Datos para las comprobaciones de F3

- **Escala:** 1 unidad CAD = 1 m (el DXF declara mm por error). Caja de muros 13,09 × 11,39 m (CAD).
- **Origen:** el mundo de Gazebo usa **coordenadas del CAD**; el modelo tiene pose = origen del mapa (4,7299; −11,32). El mapa nav2 usa el mismo origen, así que `map` y `world` coinciden **si no se aplica desplazamiento**. Esquina inferior izquierda de los muros = (4,93; −11,12); superior derecha ≈ (18,02; 0,27).
- **Orientación:** x hacia el este, y hacia el norte del dibujo; fila 0 del PGM = y máxima (convención nav2). La captura 01 es la referencia visual.
- **Aberturas:** 6 huecos libres: 4 × 0,90–0,91 m (aseos y dormitorios 1 y 2), dormitorio 3 ≈ 1,00–1,01 m, entrada oeste ≈ 1,54 m. Hueco no cerrado de ≈ 2,2 m en la zona técnica (baranda sin reconstruir) y hoja corredera (~1,9 m) como hueco libre. Ventanas dentro del muro.
- **Qué debe decidir F3:** usar el mapa de 0,02 m (pedido) o el de 0,01 m (muros +0,9 m² frente a +0,017 m²). Con 0,02 m los muros salen ~0,5 cm más gruesos por cara y las aberturas ~1 cm más estrechas que el CAD.
- **No verificado:** `sdf2map` sobre este mundo, `map_server`/RViz2, coincidencia visual Gazebo ↔ RViz2.
