#!/bin/bash
# Cek apakah headphone dicolokkan (status 1)
status=$(cat /proc/asound/card*/codec#*/eld* 2>/dev/null | grep -c "connection_type")

if [ "$status" -gt 0 ]; then
    # Ganti ke port headphone (sesuaikan nama port dari hasil pactl tadi)
    pactl set-sink-port 0 analog-output-headphones
else
    # Balik ke speaker
    pactl set-sink-port 0 analog-output-speaker
fi