@echo off
mkdir video_data
ffmpeg -i %1 -r %2 -f image2 video_data/images%%05d.png