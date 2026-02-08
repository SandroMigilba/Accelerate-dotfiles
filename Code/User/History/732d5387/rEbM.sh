#!/bin/bash

# 1. Ambil daftar koneksi yang tersimpan
chosen_conn=$(nmcli -g NAME connection show | rofi -dmenu -p "Pilih Wi-Fi:")

# Jika user menekan Esc, keluar
[ -z "$chosen_conn" ] && exit

# 2. Berikan opsi: Connect atau Delete
action=$(echo -e "Connect\nDelete" | rofi -dmenu -p "Aksi untuk $chosen_conn:")

case $action in
    Connect)
        # Menjalankan terminal untuk input password jika diperlukan
        alacritty -e nmcli connection up "$chosen_conn" --ask
        ;;
    Delete)
        nmcli connection delete "$chosen_conn" && notify-send "Terhapus" "$chosen_conn telah dibuang"
        ;;
esac