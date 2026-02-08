#!/bin/bash

# Konfigurasi Folder
WALLPAPER_DIR="$HOME/Pictures/wallpapers"
WOFI_STYLE="$HOME/.config/wofi/style.css"

# Ambil daftar file
list=$(ls $WALLPAPER_DIR)

# Tampilkan di Wofi
selected=$(echo "$list" | wofi --dmenu --prompt "Pilih Wallpaper..." --style $WOFI_STYLE --width 400 --height 400)

# Jika ada yang dipilih, pasang menggunakan swww
if [ -n "$selected" ]; then
    swww img "$WALLPAPER_DIR/$selected" --transition-type grow --transition-pos center --transition-duration 1
fi