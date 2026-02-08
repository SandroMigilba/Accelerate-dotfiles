#!/bin/bash

# Folder tempat wallpaper Anda disimpan
DIR=$HOME/Pictures/wallpapers/

# Ambil gambar secara acak
PICS=($DIR/*)
RANDOM_PIC=${PICS[$RANDOM % ${#PICS[@]}]}

# Ganti wallpaper dengan efek transisi zoom/type sesuai tema search
swww img "$RANDOM_PIC" --transition-type grow --transition-pos center --transition-duration 1.5 --transition-fps 60
