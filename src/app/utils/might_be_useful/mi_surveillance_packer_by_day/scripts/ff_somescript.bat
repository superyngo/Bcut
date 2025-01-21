@REM set speed 
ffmpeg -i 20241117_cut.mp4 -vf "setpts=0.01*PTS" -af "atempo=100" output.mkv
ffmpeg -i input.mkv -filter_complex "[0:v]setpts=0.5*PTS[v];[0:a]atempo=2[a]" -map "[v]" -map "[a]" output.mkv
ffmpeg -i 20241117_cut.mp4 -vf "setpts='if(gte(mod(N,2382),40),0.01*PTS,PTS)'" -an output.mkv
ffmpeg -i 20241117_cut.mkv -filter:v "setpts=PTS/60" output.mkv
ffmpeg -i "%~1" -vf "select='not(mod(n,100))',setpts=N/FRAME_RATE/TB" -af "aselect='not(mod(n,100)',asetpts=N/SR/TB" -shortest -vsync vfr "%~n1_%postfix%.mkv"
ffmpeg -i 20M41S_1732119641.mp4 -vf "select='not(mod(n,100))',setpts=N/FRAME_RATE/TB" -af "aselect='not(mod(n,100))',asetpts=N/SR/TB" -shortest -vsync vfr output.mkv
ffmpeg -i 20M41S_1732119641.mp4 -filter_complex "[0:v]setpts=0.01*PTS[v];[0:a]atempo=100[a]" -map "[v]" -map "[a]" output.mp4

ffmpeg -i 1.mp4 -vf "select='not(mod(n,100))',setpts=N/FRAME_RATE/TB" -af "aselect='not(mod(n,100))',asetpts=N/SR/TB" -shortest -vsync vfr -video_track_timescale 90000 -map 0 -c:v hevc -preset fast -crf 18 -c:a pcm_alaw -b:a 192k output.mkv
ffmpeg -i 1.mp4 -filter:v "select='not(mod(n,50))',setpts=N/FRAME_RATE/TB" -af "aselect='not(mod(n,50))',asetpts=N/SR/TB" -video_track_timescale 90000 -map 0 -c:v hevc -tag:v 0x31637668 -c:a pcm_alaw -ar 16000 -metadata compatible_brands=mp42,isom -metadata major_brand=mp42 -metadata:s:a handler_name="SoundHandler" -metadata:s:v handler_name="VideoHandler" -metadata encoder= -f mov output.mp4
ffmpeg -i 1.mp4 -filter:v "select='not(mod(n,2))',setpts=N/FRAME_RATE/TB" -af "aselect='not(mod(n,2))',asetpts=N/SR/TB" -video_track_timescale 90000 -map 0 -c:v hevc -tag:v 0x31637668 -b:v 921k -c:a pcm_alaw -ar 16000 -f mov output.mp4

@REM cut
ffmpeg -i input.mkv -ss 00:00:33 -to 00:01:00 -c:v copy -c:a copy output.mkv

@REM speedup by image
ffmpeg -i 20241117_cut.mkv -f image2pipe -r 0.2 - | ffmpeg -i - -an -y out.mkv

@REM jumpcut by t and speedup by n
ffmpeg -i 20241117_cut.mp4 -vf "
select='if(lte(mod(t,180),3),1,not(mod(n,100)))',setpts=N/FRAME_RATE/TB
" -af "
aselect='if(lte(mod(t,180),3),1,not(mod(n,100)))',asetpts=N/SR/TB
" -shortest output.mkv

@REM probe
ffprobe -i 1732143515.mp4

@REM set fps
ffmpeg -i 20241117_cut.mp4 -filter:v "fps=20" -c:v libx264  -preset fast -crf 23 -c:a copy output.mp4

ffmpeg -i 1.mp4 -map 0 -c:v hevc -b:v 920k -c:a pcm_alaw -ar 16000 -b:a 128k -f mov -f mov output.mp4
ffmpeg -i 1.mp4 -video_track_timescale 90000 -map 0 -c:v hevc -crf 30 -c:a pcm_alaw -ar 16000 -b:a 128k -f mov -f mov output.mp4


