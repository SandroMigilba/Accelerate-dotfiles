#!/bin/bash

# Konfigurasi
WALL_DIR="$HOME/Pictures/wallpapers"
WOFI_CONF="$HOME/.config/wofi/config"
WOFI_STYLE="$HOME/.config/wofi/style.css"

# Cek apakah folder ada
if [ ! -d "$WALL_DIR" ]; then
    notify-send "Error" "Folder wallpaper tidak ditemukan!"
    exit 1
fi

# Ambil list file dan tampilkan di Wofi
selected=$(ls "$WALL_DIR" | wofi --dmenu --conf "$WOFI_CONF" --style "$WOFI_STYLE" --prompt "Pilih Wallpaper")

# Jika user memilih salah satu file
if [ -n "$selected" ]; then
    swww img "$WALL_DIR/$selected" \
        --transition-type grow \
        --transition-pos center \
        --transition-duration 1.2 \
        --transition-fps 60
fi