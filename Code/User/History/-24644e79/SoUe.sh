#!/bin/bash

# File sementara untuk menyimpan state klik
tmp_file="/tmp/hypr_click_count"
now=$(date +%s%3N)

if [ ! -f $tmp_file ]; then
    echo "1 $now" > $tmp_file
else
    read count last_time < $tmp_file
    diff=$((now - last_time))

    # Jeda 500ms untuk menentukan double/triple click
    if [ $diff -lt 500 ]; then
        count=$((count + 1))
    else
        count=1
    fi
    echo "$count $now" > $tmp_file
fi

# Logika Eksekusi berdasarkan jumlah klik
if [ "$count" -eq 2 ]; then
    # KLIK 2x: Memindahkan Jendela (Move)
    hyprctl dispatch resizewindow 2
elif [ "$count" -eq 3 ]; then
    # KLIK 3x: Ubah ke Floating
    hyprctl dispatch togglefloating
    # Reset file agar tidak lanjut ke klik ke-4
    rm $tmp_file
fi