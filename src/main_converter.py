from pathlib import Path
from app import config
from app import mideo_converter


# from app.services import ffmpeg_converter

# file = Path(
#     r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample\cut_sl_speedup - 複製\input.mkv"
# )
# output = Path(
#     r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample\cut_sl_speedup - 複製\input_processed.mkv"
# )
# ffmpeg_converter.jumpcut(file, output, 2, 1, 1, 3)


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
