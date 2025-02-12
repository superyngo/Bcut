from math import e
from pathlib import Path
from app import constants

# from app import mideo_converter
from app.services.ffmpeg_converter import ffmpeg_converter

#

file = Path(r"H:\Projects\Python\sample\2025-01-20_1737324029_merged_cut.mkv")
file2 = Path(
    r"H:\Projects\Python\sample\tt\cut_sl_speedup\2025-01-03_1735874716_merged_cut_sl_speedup.mkv"
)
file3 = Path(r"H:\Projects\Python\sample\2025-01-20_1737324029_merged_cut_jumpcut.mkv")
file4 = Path(
    r"H:\Projects\Python\sample\2025-01-20_1737324029_merged_cut_jumpcut_keep_or_remove.mkv"
)
output_dir: Path = Path(r"H:\Projects\Python\sample\abc")
output = file.parent / f"{file.stem}_processed.mkv"

ffmpeg_converter._create_speedup_args(10)
ffmpeg_converter.speedup(file, None, 2)
ffmpeg_converter._ffmpeg(
    **ffmpeg_converter._create_full_args(
        file2, None, **ffmpeg_converter._create_speedup_args(2)
    )
)
ffmpeg_converter.cut_silence(
    file,
    None,
    -15)
    (odd_args=ffmpeg_converter._create_speedup_args(2),
    # even_args=ffmpeg_converter._create_speedup_args(10),
)

ffmpeg_converter.advanced_keep_or_remove_by_cuts(
    file,
    None,
    (
        "00:00:00",
        "00:00:05",
        "00:12:22",
        "00:14:26",
        "00:17:30",
        "00:43:44",
        "00:54:20",
        "01:03:46",
    ),
    odd_args={},
    even_args=ffmpeg_converter._create_speedup_args(50),
)
full_args = ffmpeg_converter._create_full_args(
    input_file=file,
    output_file=file.parent / (file.stem + "_processed" + file.suffix),
    **ffmpeg_converter._create_cut_args(start_time="00:00:00", end_time="00:01:00"),
    **ffmpeg_converter._create_jumpcut_args(2, 5, 0, 5),
)
ffmpeg_converter._ffmpeg(**full_args)


def main() -> None:
    target_path: Path = Path(r"D:\smb\xiaomi\xiaomi_camera_videos\94f827b4b94e")
    merge_task_info: mideo_converter.types.MideoMergerTask = {
        "folder_path": target_path,
        "start_hour": 6,
        "delete_after": True,
        "valid_extensions": {mideo_converter.types.VideoSuffix.MP4},
    }
    mideo_converter.merger_handler(**merge_task_info)

    cut_sl_speedup_task_info: mideo_converter.types.CutSlSpeedupTask = {
        "folder_path": target_path,
        "multiple": 0,
        "valid_extensions": {mideo_converter.types.VideoSuffix.MKV},
        "cut_sl_config": {"dB": -20},
    }
    mideo_converter.cut_sl_speedup_handler(**cut_sl_speedup_task_info)


if __name__ == "__main__":
    main()
