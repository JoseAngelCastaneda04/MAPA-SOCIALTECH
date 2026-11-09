#!/usr/bin/env bash
# Compila LibreDWG 0.14 (release OFICIAL de GNU, GPL-3) dentro de F1, sin instalar nada. Sin sudo, sin instalación global.
# Procedencia revisada: firma GPG de Reini Urban (mantenedor) verificada con el llavero oficial de GNU; sin binarios
# precompilados; sin acceso a red ni sudo en los scripts de build (solo un comentario dnl en configure.ac).
set -euo pipefail
F1="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$F1/herramientas/libredwg_gnu"

cd "$SRC"
# 1) la firma se vuelve a comprobar ANTES de compilar
gpgv --keyring ./gnu-keyring.gpg libredwg-0.14.tar.xz.sig libredwg-0.14.tar.xz
# 2) compilar con instalación local; sin bindings, sin documentación, sin python
cd libredwg-0.14
./configure --disable-bindings --disable-docs --disable-python > "$SRC/configure.log" 2>&1
make -j"$(nproc)" > "$SRC/make.log" 2>&1
# NO se hace "make install": libtool no soporta el espacio de "MAPA SOCIALTECH" en el prefijo (comprobado: falla).
# Los programas se usan desde el árbol de compilación (son envoltorios de libtool que funcionan igualmente):
ls "$SRC/libredwg-0.14/programs/dwg2dxf" "$SRC/libredwg-0.14/programs/dxf2dwg"
