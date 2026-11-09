#!/usr/bin/env bash
# F4: regenera TODO desde config/mobiliario.yaml: mundo Gazebo + capa de mobiliario (sdf2map) + mapa combinado + comprobaciones.
# No toca el piso, ni F0-F3. Uso: scripts/regenerar.sh [--malla]   (--malla: sillas con colision de malla original, solo para pruebas)
set -eo pipefail
D="$(cd "$(dirname "$0")/.." && pwd)"
source /opt/ros/jazzy/setup.bash; source "$D/../F1_INVESTIGACION_SOFTWARE/ws/install/setup.bash"
F2M="$D/../F2_PLANO_SIMPLE_GAZEBO/mundo/modelos"
export GZ_SIM_RESOURCE_PATH="$D/modelos:$F2M" SDF_PATH="$D/modelos:$F2M"
SFX=""; [ "${1:-}" = "--malla" ] && SFX="_malla"
read -r ZMIN ZMAX BASE < <(python3 -c "import yaml;c=yaml.safe_load(open('$D/config/mobiliario.yaml'));print(c['slice_z'][0],c['slice_z'][1],c['mapa_base'])")
python3 "$D/scripts/generar_mundo.py" ${1:+$1}
gz sdf -k "$D/mundo/piso_amueblado$SFX.sdf"
gz sdf -k "$D/mundo/solo_mobiliario$SFX.sdf"
mkdir -p "$D/mapa"
ros2 run sdf2map sdf2map --input "$D/mundo/solo_mobiliario$SFX.sdf" --output "$D/mapa/capa_mobiliario$SFX.pcd" \
   --density 40000 --occupancy-grid "$D/mapa/capa_mobiliario$SFX.yaml" --grid-resolution 0.01 --slice-z-min "$ZMIN" --slice-z-max "$ZMAX"
python3 "$D/scripts/combinar_mapas.py" --base "$D/$BASE" --nube "$D/mapa/capa_mobiliario$SFX.pcd" --z "$ZMIN" "$ZMAX" --salida "$D/mapa/piso_amueblado$SFX" --capa-alineada "$D/mapa/capa_alineada$SFX.pgm"
echo "OK: $D/mundo/piso_amueblado$SFX.sdf  $D/mapa/piso_amueblado$SFX.yaml"
