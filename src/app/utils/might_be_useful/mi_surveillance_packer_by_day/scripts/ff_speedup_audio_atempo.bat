@echo off
setlocal EnableDelayedExpansion

REM Set the speedup ratio (e.g., 2 for doubling the speed, 0.5 for half speed)
set "speedup_ratio=100"

REM Calculate the video speed-up factor (inverse of speedup_ratio for PTS)
for /f "tokens=1,2 delims=." %%a in ("%speedup_ratio%") do (
    set "integer=%%a"
    set "fraction=%%b"
)
set "video_pts=1.%fraction%/%integer%"
set "filter_complex_expr=[0:v]setpts=!video_pts!*PTS[v];[0:a]atempo=!speedup_ratio![a]" 
set "postfix=speedup"

REM Check if files were dragged and dropped
if "%~1"=="" (
    echo No files dragged. Processing all MKV files in the current folder.
    for %%F in (*.mkv) do (
        echo Processing: %%F
        ffmpeg -i "%%F" -filter_complex %filter_complex_expr% -map "[v]" -map "[a]" "%%~nF_%postfix%.mkv"
    )
) else (
    echo Files dragged. Processing pulled files.
    :process_args
    if "%~1"=="" goto :done
    echo Processing: %~1
    ffmpeg -i "%~1" -filter_complex %filter_complex_expr% -map "[v]" -map "[a]" "%~n1_%postfix%.mkv"
    shift
    goto :process_args
)
:done

echo All processing done.
pause
