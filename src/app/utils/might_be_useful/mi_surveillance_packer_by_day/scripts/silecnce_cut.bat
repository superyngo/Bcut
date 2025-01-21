ffmpeg -i output.mp4 -af silencedetect=n=-35dB:d=2.0 -f null - 2> silence.log

ffprobe -i output.mp4 -v quiet -show_entries format=duration -hide_banner -of default=noprint_wrappers=1:nokey=1
