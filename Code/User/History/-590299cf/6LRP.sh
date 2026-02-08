#!/bin/bash

WALL_DIR="$HOME/Pictures/wallpapers"
WOFI_STYLE="$HOME/.config/wofi/style.css"

# Ambil daftar file, potong jika > 20 karakter, lalu tampilkan di Wofi
# Format list: "Nama Singkat... | Nama_Asli_File.jpg"
selected=$(ls "$WALL_DIR" | awk '{
    if (length($0) > 20) 
        printf "%s... | %s\n", substr($0, 1, 17), $0
    else 
        printf "%s | %s\n", $0, $0
}' | wofi --dmenu --style "$WOFI_STYLE" --width 400 --height 450 --prompt "Pilih Wallpaper")

# Ambil bagian Nama_Asli_File.jpg (setelah tanda |)
real_file=$(echo "$selected" | awk -F ' | ' '{print $NF}')

if [ -n "$real_file" ]; then
    swww img "$WALL_DIR/$real_file" \
        --transition-type grow \
        --transition-pos center \
        --transition-duration 1.2
fi