#!/bin/bash

# File sementara untuk menghitung klik
tmp_file="/tmp/hypr_click_count"
now=$(date +%s%3N) # Waktu dalam milidetik

if [ ! -f $tmp_file ]; then
    echo "1 $now" > $tmp_file
else
    read count last_time < $tmp_file
    diff=$((now - last_time))

    # Jika jeda antar klik < 500ms, tambahkan hitungan
    if [ $diff -lt 500 ]; then
        count=$((count + 1))
    else
        count=1
    fi
    echo "$count $now" > $tmp_file
fi

# Logika Aksi
if [ "$count" -eq 2 ]; then
    # Klik Kanan 2x: Pindah Jendela
    hyprctl dispatch movewindow
elif [ "$count" -eq 3 ]; then
    # Klik Kanan 3x: Toggle Floating
    hyprctl dispatch togglefloating
    rm $tmp_file # Reset hitungan setelah aksi terpenuhi
fi