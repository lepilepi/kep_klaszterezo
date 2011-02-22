#!/bin/bash
if [ -z "$1" ]; then
    echo usage: not enough parameters
    exit
fi
if [ -z "$2" ]; then
    frames=1;
else
    frames=$2;
fi
if [ -z "$3" ]; then
    repeat=1;
else
    repeat=$3;
fi
mkdir video_data
ffmpeg -i $1 -r $frames -f image2 video_data/images%05d.png
python main.py -v -i -r $repeat -d video_data/images*
