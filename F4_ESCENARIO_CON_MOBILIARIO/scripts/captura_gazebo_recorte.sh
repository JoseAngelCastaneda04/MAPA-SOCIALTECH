#!/usr/bin/env bash
# F4: como captura_gazebo.sh pero recorta la franja superior (barra de titulo, 62 px) para que no entren avisos de escritorio ajenos.
# Uso: captura_gazebo_recorte.sh <pid_gz_gui> <salida.png>
D="$(cd "$(dirname "$0")" && pwd)"; T=$(mktemp --suffix=.png)
"$D/captura_gazebo.sh" "$1" "$T" || exit $?
python3 -c "
from PIL import Image; im=Image.open('$T'); im.crop((0,62,im.width,im.height)).save('$2')"; rm -f "$T"; echo "recortado -> $2"
