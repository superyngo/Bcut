from ...utils import logger
from ...services import ffmpeg_converter
from .types import CutSlConfig, VideoSuffix
import os
from datetime import datetime, timedelta, date
from typing import TypedDict
from pathlib import Path
import re

__all__: list[str] = ["merger_handler", "cut_sl_speedup_handler"]


class HandleSpeedup(TypedDict):
    start_hour: int
    end_hour: int


def _extract_epoch(filename: Path | str) -> int | None:
    """Function to extract the first valid 10-digit epoch time from filename using regex"""

    try:
        # Regex pattern to find a sequence of exactly 10 digits
        matches = re.findall(r"\D?(\d{10})\D?", str(Path(filename).stem))
        if matches:
            return int(matches[0])
        else:
            logger.error(f"No valid 10-digit epoch time found in {filename}")
            return None
    except ValueError as e:
        logger.error(f"Failed to extract epoch from {filename}: {str(e)}")
        return None


def _list_video_files(
    root_path: str | Path,
    valid_extensions: set[VideoSuffix] | None = None,
    walkthrough: bool = True,
) -> list[Path]:
    if valid_extensions is None:
        valid_extensions = set(
            suffix for suffix in VideoSuffix
        )  # Add more extensions as needed

    root_path = Path(root_path)
    video_files: list[Path] = []

    # Use rglob to recursively find files with the specified extensions
    video_files = (
        [
            file
            for file in root_path.rglob("*")
            if file.is_file() and file.suffix.lstrip(".").lower() in valid_extensions
        ]
        if walkthrough
        else [
            file
            for file in root_path.iterdir()
            if file.is_file() and file.suffix.lstrip(".").lower() in valid_extensions
        ]
    )

    return video_files


# def get_speedup_range(start_hour: int, end_hour: int) -> range | list[int]:
#     # Create the speedup range, handling wrap-around at midnight
#     if end_hour >= start_hour:
#         return range(start_hour, end_hour + 1)
#     else:
#         return list(range(start_hour, 25)) + list(range(0, end_hour + 1))


type GroupedVideos = dict[date, dict[int, Path]]


def _group_files_by_date(video_files: list[Path], start_hour: int = 0) -> GroupedVideos:
    grouped_files: GroupedVideos = {}

    for video_path in video_files:
        filename: str = os.path.basename(video_path)
        epoch_time: int | None = _extract_epoch(filename)
        date_key: str | date

        if epoch_time is None:
            logger.warning(f"skip {filename} with no time.")
            continue
        else:
            file_datetime: datetime = datetime.fromtimestamp(epoch_time)
            if file_datetime.hour < start_hour:
                file_datetime -= timedelta(days=1)
            date_key = file_datetime.date()

        if date_key not in grouped_files:
            grouped_files[date_key] = {}
        grouped_files[date_key].update({epoch_time: video_path})

    return grouped_files


def _merge_videos(
    video_dict: GroupedVideos, save_path: Path, delete_after: bool, **otherkwargs
) -> int:
    """_summary_

    Args:
        video_dict (GroupedVideos): _description_
        save_path (Path): _description_
        delete_after (bool): _description_

    Returns:
        int: _description_
    """
    today: date = datetime.today().date()
    dir_to_delete: set[Path] = set()

    for date_key, videos in video_dict.items():

        if date_key == today:
            logger.info(f"Skipping today's date: {date_key}")
            continue

        # Sort the videos by epoch time
        sorted_videos = dict(sorted(videos.items()))

        # Prepare the input file list with valid check for ffmpeg
        input_files: list[Path] = []
        for video_path in sorted_videos.values():
            if ffmpeg_converter.is_valid_video(video_path):
                input_files.append(video_path)
                dir_to_delete.add(video_path.parent)

        if not input_files:
            logger.info(f"No valid videos found for {date_key}. Skipping.")
            continue

        # Write the input file list for ffmpeg
        temp_input: Path = Path(r"input.txt")
        with open(temp_input, "w", encoding="utf-8") as f:
            for file in input_files:
                f.write(f"file '{file}'\n")

        # Get the file's timestamp to the first video's epoch time
        first_video_epoch = next(iter(sorted_videos))

        # Define the output file path
        output_file: Path = save_path / f"{date_key}_{first_video_epoch}_merged.mkv"
        logger.info(f"{output_file = }")
        try:
            # Use ffmpeg to concatenate videos
            ffmpeg_converter.merge(temp_input, output_file, **otherkwargs)
        except ffmpeg_converter.ffmpeg_Error as e:
            logger.error(
                f"Failed to concatenate videos for {date_key}. Error: {e.stderr.decode()}"
            )
            return 1

        # Remove the temporary input file list
        os.remove(temp_input)

        os.utime(output_file, (first_video_epoch, first_video_epoch))

        # Clean up original video files and directories
        logger.info("Deleting source videos.")
        if delete_after:
            try:
                for video_path in sorted_videos.values():
                    os.remove(video_path)
                for dir in dir_to_delete:
                    os.rmdir(dir)
            except OSError as e:
                logger.error(
                    f"Failed to delete files or directories for {date_key}: {str(e)}"
                )
                return 2
        dir_to_delete.clear()

        logger.info(
            f"Processed {date_key}, saved to {output_file}, set timestamps, and deleted original files."
        )

    return 0


def merger_handler(
    folder_path: Path,
    start_hour: int = 6,
    delete_after: bool = True,
    valid_extensions: set[str] | None = None,
    **otherkwargs,
) -> int:
    """_summary_

    Args:
        folder_path (Path): _description_
        start_hour (int, optional): _description_. Defaults to 6.
        delete_after (bool, optional): _description_. Defaults to True.

    Returns:
        int: _description_
    """
    logger.info(f"Start merging videos in {folder_path}")

    video_files: list[Path] = _list_video_files(
        folder_path, valid_extensions=valid_extensions
    )
    if not video_files:
        logger.info(f"No {valid_extensions} files in {folder_path}")
        return 1

    grouped_videos: GroupedVideos = _group_files_by_date(video_files, start_hour)

    do_merge: int = _merge_videos(
        grouped_videos, folder_path, delete_after, **otherkwargs
    )

    return do_merge


def _cut_sl_speedup(
    input_folder: Path,
    multiple: int | float = 0,
    same_encode: bool = True,
    output_folder_name: str = "cut_sl_speedup",
    valid_extensions: set[str] | None = None,
    cut_sl_config: CutSlConfig | None = None,
    **otherkwargs,
):
    """_summary_

    Args:
        input_folder (Path): _description_
        multiple (int | float): _description_
        same_encode (bool, optional): _description_. Defaults to True.
        output_folder_name (str, optional): _description_. Defaults to "cut_sl_speedup".

    Returns:
        _type_: _description_
    """
    video_files: list[Path] = _list_video_files(input_folder, valid_extensions, False)
    if not video_files:
        logger.info(f"no {valid_extensions} files in {input_folder}")
        return 1

    if cut_sl_config is None:
        cut_sl_config = {}

    output_folder: Path = input_folder / output_folder_name
    output_folder.mkdir(parents=True, exist_ok=True)

    for video in video_files:
        # Get the file's timestamp to the first video's epoch time
        video_epoch = _extract_epoch(video)

        output_file: Path = output_folder / (
            video.stem + "_" + output_folder_name + video.suffix
        )

        cut_silence = ffmpeg_converter.cut_silence(video, output_file, **cut_sl_config)

        if cut_silence != 0:
            logger.error(f"Failed to cut silence for {video}. Skipping.")
            continue

        if multiple != 0:
            original_encode: ffmpeg_converter.types.EncodeKwargs = (
                (ffmpeg_converter.probe_encoding_info(video)) if same_encode else {}
            )

            ffmpeg_converter.speedup(
                output_file, output_file, multiple, **(original_encode | otherkwargs)
            )
        else:
            logger.info(f"{multiple = } for {video}. No sppedup.")

        if video_epoch:
            os.utime(output_file, (video_epoch, video_epoch))

        logger.info(
            f"Cut silence and speeding up video saved to {output_file}, set timestamps as the original file."
        )

    return 0


def cut_sl_speedup_handler(
    folder_path: Path,
    multiple: int | float = 2,
    valid_extensions: set[str] | None = None,
    cut_sl_config: CutSlConfig | None = None,
    **otherkwargs,
) -> int:
    """_summary_

    Args:
        folder_path (Path): _description_
        multiple (int, optional): _description_. Defaults to 50.

    Returns:
        int: _description_
    """
    logger.info(f"Start cutting silence and speed up videos in {folder_path}")

    if cut_sl_config is None:
        cut_sl_config = {}

    defalut_cut_sl_config: CutSlConfig = {
        "dB": -25,
        "sl_duration": 0.1,
        "seg_min_duration": 0,
    }

    do_cut_si_speedup: int = _cut_sl_speedup(
        folder_path,
        multiple,
        valid_extensions=valid_extensions,
        cut_sl_config=defalut_cut_sl_config | cut_sl_config,
        **otherkwargs,
    )

    return do_cut_si_speedup


def main() -> None:
    pass


if __name__ == "__main__":
    main()
