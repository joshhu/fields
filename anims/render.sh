#!/usr/bin/env bash
# usage: ./render.sh <name>  (run inside anims/)
set -e
n="$1"
uv run manim -qh --fps 30 --disable_caching --media_dir ../build/manim -o "$n.mp4" "$n.py" Main >"../build/manim_$n.log" 2>&1 || { tail -30 "../build/manim_$n.log"; exit 1; }
mkdir -p ../assets/anim
cp "../build/manim/videos/$n/1080p30/$n.mp4" "../assets/anim/$n.mp4"
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "../assets/anim/$n.mp4")
ffmpeg -v error -y -ss $(python -c "print($d/2)") -i "../assets/anim/$n.mp4" -frames:v 1 "../build/check_$n.png"
echo "$n $d"
