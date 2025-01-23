from pathlib import Path
from app import constants
from app import mideo_converter
from app import ffmpeg_converter

#

file = Path(r"F:\Projects\Python\sample\2025-01-20_1737324029_merged_cut.mkv")
output = file.parent / f"{file.stem}_processed.mkv"
code = ffmpeg_converter.probe_encoding_info(file)
ffmpeg_converter.is_valid_video(file)
ffmpeg_converter.cut_silence_rerender(file, output, -15, **code)


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
