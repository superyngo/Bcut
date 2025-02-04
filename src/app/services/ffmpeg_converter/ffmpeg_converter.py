# import ffmpeg
from typing import Literal, OrderedDict, Sequence
from pathlib import Path
from enum import StrEnum, auto
from collections import deque
from collections.abc import Generator
import re
import subprocess
from enum import Enum
import tempfile
import time
import os
import concurrent.futures
import json
from decimal import Decimal, ROUND_CEILING
from .types import EncodeKwargs, VideoSuffix
from app.common import logger


class _methods(StrEnum):
    SPEEDUP = auto()
    JUMPCUT = auto()
    CONVERT = auto()
    CUT = auto()
    KEEP_OR_REMOVE = auto()
    MERGE = auto()
    PROBE_ENCODING = auto()
    PROBE_DURATION = auto()
    probe_is_valid_video = auto()
    probe_non_silence = auto()
    CUT_SILENCE = auto()
    CUT_SILENCE_RERENDER = auto()


def _dic_to_ffmpeg_args(kwargs: dict | None = None) -> str:
    if kwargs is None:
        return ""
    return " ".join(f"-{key} {value}" for key, value in kwargs.items())


def _ffmpeg(**kwargs):
    default_kwargs = {"loglevel": "warning"}
    output_kwargs: dict = kwargs
    logger.info(f"Execute FFmpeg with {output_kwargs = }")
    command = ["ffmpeg"] + _dic_to_ffmpeg_args(kwargs | default_kwargs).split()
    subprocess.run(command, check=True)


def _gen_filter(
    filter_text: Sequence[str],
    videoSectionTimings: Sequence[float],
) -> Generator[str, None, None]:
    yield filter_text[0]
    yield from (
        f"between(t,{videoSectionTimings[i]},{videoSectionTimings[i + 1]})"
        + ("+" if i != len(videoSectionTimings) - 2 else "")
        for i in range(0, len(videoSectionTimings), 2)
    )
    yield filter_text[1]


def _ffprobe(**kwargs):
    output_kwargs: dict = kwargs
    logger.info(f"Execute ffprobe with {output_kwargs = }")
    command: str = f"ffprobe {_dic_to_ffmpeg_args(kwargs)}"
    subprocess.run(command, shell=True, check=True)


def probe_duration(input_file: Path, **othertags) -> float:  # command
    output_kwargs: dict = {
        "v": "error",
        "show_entries": "format=duration",
        "of": "default=noprint_wrappers=1:nokey=1",
        "i": f'"{input_file}"',
    } | othertags
    logger.info(f"Probing {input_file.name} duration with {output_kwargs = }")
    command: str = f"ffprobe {_dic_to_ffmpeg_args(output_kwargs)}"
    probe_duration = os.popen(command).read().strip()
    logger.info(f"{input_file.name} duration probed: {probe_duration}")

    return float(probe_duration)


def probe_encoding(input_file: Path, **othertags) -> EncodeKwargs:  # command
    output_kwargs: dict = {
        "v": "error",
        "print_format": "json",
        "show_format": "",
        "show_streams": "",
        "i": f'"{input_file}"',
    } | othertags
    logger.info(f"Probing {input_file.name} encoding with {output_kwargs = }")
    # Probe the video file to get metadata
    command: str = f"ffprobe {_dic_to_ffmpeg_args(output_kwargs)}"
    probe = os.popen(command).read().encode("utf-8").decode("utf-8")
    probe = json.loads(probe)

    # Initialize the dictionary with default values
    encoding_info: EncodeKwargs = {}

    # Extract video stream information
    video_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "video"), None
    )
    if video_stream:
        encoding_info["video_track_timescale"] = int(
            video_stream.get("time_base").split("/")[1]
        )
        encoding_info["vcodec"] = video_stream.get("codec_name")
        encoding_info["video_bitrate"] = int(video_stream.get("bit_rate", 0))

    # Extract audio stream information
    audio_stream = next(
        (stream for stream in probe["streams"] if stream["codec_type"] == "audio"), None
    )
    if audio_stream:
        encoding_info["acodec"] = audio_stream.get("codec_name")
        encoding_info["ar"] = int(audio_stream.get("sample_rate", 0))

    # Extract format information
    format_info = probe.get("format", {})
    encoding_info["f"] = format_info.get("format_name").split(",")[0]
    cleaned_None = {k: v for k, v in encoding_info.items() if v is not None and v != 0}
    logger.info(f"{input_file.name} probed: {cleaned_None}")

    return cleaned_None  # type: ignore


def probe_non_silence(  # command
    input_file: Path, dB: int = -35, sl_duration: float = 1, **othertags
) -> tuple[Sequence[float], float, float]:
    """_summary_

    Args:
        input_file (Path): _description_
        dB (int, optional): _description_. Defaults to -35.
        sl_duration (float, optional): _description_. Defaults to 1.

    Returns:
        tuple[Sequence[float], float, float]: (non_silence_segs, total_duration, total_silence_duration)
    """
    output_kwargs: dict = (
        {
            "i": f'"{input_file}"',
            "af": f"silencedetect=n={dB}dB:d={sl_duration}",
            "f": "null",
        }
        | othertags
        | {"": ""}
    )

    logger.info(
        f"Detecting silences of {input_file.name} by {dB = } and {output_kwargs = }"
    )

    command: str = f"ffmpeg {_dic_to_ffmpeg_args(output_kwargs)}"
    output = os.popen(command + " 2>&1").read()

    # Total duration
    total_duration_pattern = r"Duration: (.+?),"
    total_duration_match: str | None = re.findall(total_duration_pattern, output)[0]
    total_duration: float = _convert_timestamp_to_seconds(
        total_duration_match if total_duration_match else "0.0"
    )

    # Regular expression to find all floats after "silence_start or end: "
    silence_seg_pattern = r"silence_(?:start|end): ([0-9.]+)"
    # Find all matches in the log data
    silence_seg_matches: list[str] = re.findall(silence_seg_pattern, output)
    # Convert matches to a list of floats
    non_silence_segs: deque[float] = deque(
        float(match) for match in silence_seg_matches
    )
    # Handle silence start and end to represent non silence
    non_silence_segs.appendleft(0.0)
    non_silence_segs.append(total_duration)

    # Regular expression to find all floats after silence_duration: "
    silence_duration_pattern = r"silence_duration: ([0-9.]+)"
    silence_duration_maches: list[str] = re.findall(silence_duration_pattern, output)
    silence_duration_matches: Generator[float] = (
        float(s) for s in silence_duration_maches
    )
    total_silence_duration: float = sum(silence_duration_matches)

    return (non_silence_segs, total_duration, total_silence_duration)


def probe_is_valid_video(input_file: Path, **othertags) -> bool:  # command
    """Function to check if a video file is valid using ffprobe."""
    output_kwargs: dict = {
        "v": "error",
        "show_entries": "format=duration",
        "of": "default=noprint_wrappers=1:nokey=1",
        "i": f'"{input_file}"',
    } | othertags
    logger.info(f"Validate {input_file.name} with {output_kwargs = }")
    try:
        command: str = f"ffprobe {_dic_to_ffmpeg_args(output_kwargs)}"
        result = os.popen(command).read().strip()
        if result:
            message = f"Checking file: {input_file}, Status: Valid"
            logger.info(message)
            return True
        else:
            message = f"Checking file: {input_file}, Status: Invalid"
            logger.info(message)
            return False
    except Exception as e:
        message = f"Checking file: {input_file}, Error: {str(e)}"
        logger.info(message)
        return False


def _probe_keyframe(input_file: Path, **othertags) -> list[float]:  # command
    output_kwargs: dict = {
        "v": "error",
        "select_streams": "v:0",
        "show_entries": "packet=pts_time,flags",
        "of": "json",
        "i": f'"{input_file}"',
    } | othertags
    logger.info(f"Get keyframe for {input_file.name} with {output_kwargs = }")
    command: str = f"ffprobe {_dic_to_ffmpeg_args(output_kwargs)}"
    probe = os.popen(command).read().encode("utf-8").decode("utf-8")
    probe = json.loads(probe)
    keyframe_pts: list[float] = [
        float(packet["pts_time"])
        for packet in probe["packets"]
        if "K" in packet["flags"]
    ]
    return keyframe_pts


def _create_force_keyframes_args(keyframe_times: int = 2) -> dict[str, str]:
    return {"force_key_frames": f'"expr:gte(t,n_forced*{keyframe_times})"'}


def _create_speedup_args(multiple: float) -> dict[str, str]:
    SPEEDUP_METHOD_THRESHOLD: int = 4
    vf: str
    af: str
    if multiple > SPEEDUP_METHOD_THRESHOLD:
        vf = f"select='not(mod(n,{multiple}))',setpts=N/FRAME_RATE/TB"
        af = f"aselect='not(mod(n,{multiple}))',asetpts=N/SR/TB"
    else:
        vf = f"setpts={1/multiple}*PTS"
        af = f"atempo={multiple}"
    return (
        {"vf": vf, "af": af}
        | {
            "map": 0,
            "shortest": "",
            "fps_mode": "vfr",
            "async": 1,
        }
        | _create_force_keyframes_args()
    )


def speedup(  # command
    input_file: Path,
    output_file: Path | None,
    multiple: float | int,
    **othertags,
) -> int:
    """_summary_

    Args:
        input_file (Path): _description_
        output_file (Path | None): _description_
        multiple (float | int): _description_

    Raises:
        e: _description_

    Returns:
        int: _description_
    """
    if multiple <= 0:
        logger.error(f"Speedup factor must be greater than 0.")
        return 1

    if output_file is None:
        output_file = input_file.parent / (
            input_file.stem + "_" + _methods.SPEEDUP + input_file.suffix
        )

    if multiple == 1:
        if input_file != output_file:
            input_file.replace(output_file)
        logger.error(f"Speedup factor 1, only replace target file")
        return 0

    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )

    output_kwargs: dict = (
        {"i": f'"{input_file}"'}
        | _create_speedup_args(multiple)
        | othertags
        | {"y": f'"{temp_output_file}"'}
    )

    logger.info(
        f"{_methods.SPEEDUP} {input_file.name} to {output_file.name} by {multiple = } with {output_kwargs = }"
    )

    try:
        _ffmpeg(**output_kwargs)
        temp_output_file.replace(output_file)
    except Exception as e:
        logger.error(
            f"Failed to {_methods.SPEEDUP} videos for {input_file}. Error: {str(e)}"
        )
        raise e
    return 0


def _create_jumpcut_args(
    interval: float,
    lasting: float,
    interval_multiple: int = 0,  # 0 means unwanted cut out
    lasting_multiple: int = 1,  # 0 means unwanted cut out
) -> dict[str, str]:
    interval_multiple_expr: str = (
        str(interval_multiple)
        if interval_multiple == 0
        else f"not(mod(n,{interval_multiple}))"
    )
    lasting_multiple_expr: str = (
        str(lasting_multiple)
        if lasting_multiple == 0
        else f"not(mod(n,{lasting_multiple}))"
    )
    frame_select_expr: str = (
        f"if(lte(mod(t, {interval + lasting}),{interval}), {interval_multiple_expr}, {lasting_multiple_expr})"
    )
    args: dict[str, str] = (
        {
            "vf": f"\"select='{frame_select_expr}',setpts=N/FRAME_RATE/TB\"",
            "af": f"\"aselect='{frame_select_expr}',asetpts=N/SR/TB\"",
        }
        | {
            "map": 0,
            "shortest": "",
            "fps_mode": "vfr",
            "async": 1,
        }
        | _create_force_keyframes_args()
    )

    return args


def jumpcut(  # command
    input_file: Path,
    output_file: Path | None,
    interval: float,
    lasting: float,
    interval_multiple: int = 0,  # 0 means unwanted cut out
    lasting_multiple: int = 1,  # 0 means unwanted cut out
    **othertags,
) -> int:
    if any((interval <= 0, lasting <= 0)):
        logger.error(f"Both 'interval' and 'lasting' must be greater than 0.")
        return 1

    if any((interval_multiple < 0, lasting_multiple < 0)):
        logger.error(
            f"Both 'interval_multiple' and 'lasting_multiple' must be greater or equal to 0."
        )
        return 2

    if output_file is None:
        output_file = input_file.parent / (
            input_file.stem + "_" + _methods.JUMPCUT + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )

    output_kwargs = _create_full_args(
        input_file=input_file,
        output_file=temp_output_file,
        **_create_jumpcut_args(interval, lasting, interval_multiple, lasting_multiple),
        **othertags,
    )

    logger.info(
        f"{_methods.JUMPCUT} {input_file.name} to {output_file.name} with {output_kwargs = }"
    )
    try:
        _ffmpeg(**output_kwargs)
        temp_output_file.replace(output_file)
    except Exception as e:
        logger.error(
            f"Failed to {_methods.JUMPCUT} videos for {input_file}. Error: {str(e)}"
        )
        return 2
    return 0


def convert(input_file: Path, output_file: Path | None, **othertags) -> int:  # command
    if output_file is None:
        output_file = input_file.parent / (
            input_file.stem + "_" + _methods.CONVERT + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )

    output_kwargs: dict = (
        {
            "i": f'"{input_file}"',
        }
        | othertags
        | {"y": f'"{temp_output_file}"'}
    )

    logger.info(
        f"{_methods.CONVERT} {input_file.name} to {output_file.name} with {output_kwargs = }"
    )
    try:
        _ffmpeg(**output_kwargs)
        temp_output_file.replace(output_file)
    except Exception as e:
        logger.error(f"Failed to convert videos for {input_file}. Error: {e}")
        raise e
    return 0


def create_merge_txt(
    video_files_source: Path | list[Path], output_txt: Path | None = None
) -> Path:
    # Step 0: Set the output txt path
    if output_txt is None:
        temp_output_dir = Path(tempfile.mkdtemp())
        output_txt = temp_output_dir / "input.txt"

    if isinstance(video_files_source, Path):
        video_files: list[Path] = sorted(
            video
            for video in video_files_source.glob("*")
            if video.suffix.lstrip(".") in VideoSuffix
        )
    else:
        video_files = video_files_source

    # Step 5: Create input.txt for FFmpeg concatenation
    with open(output_txt, "w") as f:
        for video_path in video_files:
            f.write(f"file '{video_path}'\n")

    return output_txt


def merge(input_txt: Path, output_file: Path, **othertags) -> int:  # command
    logger.info(f"{_methods.MERGE} {input_txt} to {output_file} with {othertags = }")
    output_kwargs: dict = (
        {
            "f": "concat",
            "safe": 0,
            "i": input_txt,
            "c:a": "copy",
            "c:v": "copy",
        }
        | othertags
        | {"y": output_file}
    )
    logger.info(
        f"{_methods.MERGE} {input_txt.name} to {output_file.name} with {output_kwargs = }"
    )
    try:
        _ffmpeg(**output_kwargs)
        return 0
    except Exception as e:
        logger.error(f"Failed merging {input_txt}. Error: {str(e)}")
        raise e


def _convert_seconds_to_timestamp(seconds: float | Decimal) -> str:
    """Converts seconds to HH:MM:SS format."""
    # seconds = Decimal(str(seconds)).quantize(Decimal("0.001"), rounding=ROUND_CEILING)
    # Convert seconds to hours, minutes, and seconds
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    timestamp = f"{hours:02}:{minutes:02}:{secs:02}.{milliseconds:03}"
    return timestamp


def _convert_timestamp_to_seconds(timestamp: str) -> float:
    # Split the timestamp into its components
    parts = timestamp.split(":")

    # Convert each part to a float and calculate the total seconds
    hours = float(parts[0])
    minutes = float(parts[1])
    seconds = float(parts[2])

    # Calculate total seconds
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds


def _adjust_segments_to_keyframes(
    video_segments: Sequence[float], keyframe_times: Sequence[float]
) -> Sequence[float]:
    adjusted_segments = []
    keyframe_index = 0

    for i, time in enumerate(video_segments):
        if i % 2 == 0:  # start time
            # 找到不大於當前時間的最大關鍵幀時間
            while (
                keyframe_index < len(keyframe_times)
                and keyframe_times[keyframe_index] <= time
            ):
                keyframe_index += 1
            adjusted_time = (
                keyframe_times[keyframe_index - 1] if keyframe_index > 0 else time
            )
            adjusted_segments.append(adjusted_time)
        else:  # end time
            # 找到不小於當前時間的最小關鍵幀時間
            while (
                keyframe_index < len(keyframe_times)
                and keyframe_times[keyframe_index] < time
            ):
                keyframe_index += 1
            adjusted_time = (
                keyframe_times[keyframe_index]
                if keyframe_index < len(keyframe_times)
                else time
            )
            adjusted_segments.append(adjusted_time)

    return adjusted_segments


def _ensure_minimum_segment_length(
    video_segments: Sequence[float],
    seg_min_duration: float = 1,
    total_duration: float | None = None,
) -> Sequence[float]:
    """
    Ensures that every segment in the video_segments list is at least seg_min_duration seconds long.

    Args:
        video_segments (list[float]): List of start and end times in seconds.
        seg_min_duration (float, optional): Minimum duration for each segment in seconds. Defaults to 2.

    Raises:
        ValueError: If video_segments does not contain pairs of start and end times.

    Returns:
        list[float]: Updated list of start and end times with adjusted segment durations.
    """
    if seg_min_duration == 0 or video_segments == []:
        return video_segments

    if seg_min_duration < 0:
        raise ValueError(
            f"seg_min_duration must greater than 0 but got {seg_min_duration}."
        )

    if len(video_segments) % 2 != 0:
        raise ValueError("video_segments must contain pairs of start and end times.")

    if total_duration is None:
        total_duration = video_segments[-1]

    updated_segments = []
    for i in range(0, len(video_segments), 2):
        start_time = video_segments[i]
        end_time = video_segments[i + 1]
        duration = end_time - start_time

        if duration >= seg_min_duration or len(video_segments) == 2:
            updated_segments.extend([start_time, end_time])
            continue

        if i == len(video_segments) - 2:
            # This is the last segment
            start_time = max(0, end_time - seg_min_duration)
        else:
            # Calculate the difference between the minimum duration and the current duration
            diff = seg_min_duration - duration
            # Adjust the start and end times to increase the duration to the minimum
            start_time = max(0, start_time - diff / 2)
            end_time = min(start_time + seg_min_duration, total_duration)

        updated_segments.extend([start_time, end_time])

    # Ensure the hole video is long enough
    if updated_segments[-1] - updated_segments[0] < seg_min_duration:
        return []

    return updated_segments


def _merge_overlapping_segments(segments: Sequence[float]) -> Sequence[float]:
    """_summary_

    Args:
        segments (Sequence[float]): _description_

    Returns:
        Sequence[float]: _description_
    """
    # Sort segments by start time
    sorted_segments = sorted(
        (segments[i], segments[i + 1]) for i in range(0, len(segments), 2)
    )
    if len(sorted_segments) == 0:
        return []

    merged_segments = []
    current_start, current_end = sorted_segments[0]

    for start, end in sorted_segments[1:]:
        if start <= current_end:
            # Overlapping segments, merge them
            current_end = max(current_end, end)
        else:
            # No overlap, add the current segment and move to the next
            merged_segments.extend([current_start, current_end])
            current_start, current_end = start, end

    # Add the last segment
    merged_segments.extend([current_start, current_end])

    return merged_segments


def _create_full_args(
    input_file: Path, output_file: Path | None = None, **othertags
) -> dict[str, str]:
    if output_file is None:
        output_file = input_file.parent / (
            input_file.stem + "_" + _methods.CUT + input_file.suffix
        )
    args: dict[str, str] = (
        {"i": f'"{input_file}"'} | othertags | {"y": f'"{output_file}"'}
    )
    return args


def _create_cut_args(start_time: str, end_time: str) -> dict[str, str]:
    return {
        "ss": start_time,
        "to": end_time,
    }


def cut(  # command
    input_file: Path,
    output_file: Path | None,
    start_time: str,
    end_time: str,
    rerender: bool = False,
    **othertags: EncodeKwargs,
) -> int:
    """Cut a video file using ffmpeg-python.

    Raises:
        e: _description_

    Returns:
        _type_: _description_
    """
    if output_file is None:
        output_file = input_file.parent / (
            input_file.stem + "_" + _methods.CUT + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )

    output_kwargs: dict = (
        {
            "i": f'"{input_file}"',
        }
        | _create_cut_args(start_time, end_time)
        | {
            "map": 0,
        }
        | (
            {
                "c:a": "copy",
                "c:v": "copy",
            }
            if not rerender
            else {}
        )
        | othertags
        | {"y": f'"{temp_output_file}"'}
    )
    logger.info(
        f"{_methods.CUT} {input_file.name} to {output_file.name} with {output_kwargs = }"
    )
    try:
        _ffmpeg(**output_kwargs)
        temp_output_file.replace(output_file)
    except Exception as e:
        logger.error(f"Failed to cut videos for {input_file}. Error: {e}")
        raise e
    return 0


def _split_segments_cut(
    input_file: Path,
    video_segments: Sequence[float] | Sequence[str],
    output_dir: Path | None = None,
    **othertags,
) -> tuple[Sequence[Path], Path]:
    """_summary_

    Args:
        input_file (Path): _description_
        video_segments (Sequence[float] | Sequence[str]): _description_
        output_dir (Path | None, optional): _description_. Defaults to None.

    Raises:
        ValueError: _description_

    Returns:
        tuple[Sequence[Path], Path]: (cut_videos, input_txt_path)
    """

    # Step 1: Validate input
    if len(video_segments) % 2 != 0:
        raise ValueError(
            "video_segments must contain an even number of elements (start and end times)."
        )

    # Step 2: Create a temporary folder for storing cut videos
    if output_dir is None:
        output_dir = input_file.parent / f"{input_file.stem}_segments"
    cut_videos: list[Path] = []  # List to store paths of cut video segments

    # Step 3: Use threading to process video segments
    # Get the number of CPU cores
    num_cores = os.cpu_count()

    # Use ThreadPoolExecutor to manage the threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        for i in range(0, len(video_segments), 2):
            if isinstance(video_segments[i], float):
                start_time = _convert_seconds_to_timestamp(
                    video_segments[i]  # type:ignore
                )
                end_time = _convert_seconds_to_timestamp(
                    video_segments[i + 1]  # type:ignore
                )
            else:
                start_time: str = video_segments[i]  # type:ignore
                end_time: str = video_segments[i + 1]  # type:ignore
            if start_time == end_time:
                continue
            output_file: Path = output_dir / f"{i // 2}{input_file.suffix}"
            cut_videos.append(output_file)

            # Submit the cut task to the executor
            future = executor.submit(
                cut, input_file, output_file, start_time, end_time, **othertags
            )
            futures.append(future)

        # Optionally, wait for all futures to complete
        concurrent.futures.wait(futures)

    # Step 4: Sort the cut video paths by filename (index order)
    cut_videos.sort(key=lambda video_file: int(video_file.stem))

    # Step 5: Create input.txt for FFmpeg concatenation
    input_txt_path: Path = output_dir / "input.txt"
    with open(input_txt_path, "w") as f:
        for video_path in cut_videos:
            f.write(f"file '{video_path}'\n")
    return (cut_videos, input_txt_path)


def keep_or_remove_by_cuts(
    input_file: Path,
    output_file: Path | None,
    video_segments: Sequence[str] | Sequence[float],
    keep_handle: bool = True,  # True means keep, False means remove
):
    if output_file is None:
        output_file = input_file.parent / (
            input_file.stem + "_" + _methods.KEEP_OR_REMOVE + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )
    logger.info(f"{_methods.KEEP_OR_REMOVE} {input_file.name} to {output_file.name}")

    # Step 0: Create a temporary folder for storing cut videos
    temp_dir: Path = Path(tempfile.mkdtemp())

    # Step 1:convert video segments if needed
    video_segments = deque(
        _convert_timestamp_to_seconds(s) if isinstance(s, str) else s
        for s in video_segments
    )

    # Step 2: rearrange video_segments if keep_handle == False
    if not keep_handle:
        video_segments.appendleft(0.0)
        video_segments.append(probe_duration(input_file))

    # Step 3: Cut the video into segments based on the provided start and end times
    cut_videos: Sequence[Path]
    input_txt_path: Path
    cut_videos, input_txt_path = _split_segments_cut(
        input_file,
        video_segments,
        temp_dir,
    )

    # Step 4: Merge the kept segments
    try:
        merge(input_txt_path, temp_output_file)
        temp_output_file.replace(output_file)
        # Step 5: Clean up temporary files
        for video_path in cut_videos:
            os.remove(video_path)
        os.remove(input_txt_path)
        os.rmdir(temp_dir)
    except Exception as e:
        logger.error(
            f"Failed to {_methods.KEEP_OR_REMOVE} for {input_file}. Error: {e}"
        )
        return 1
    return 0


def advanced_keep_or_remove_by_cuts(
    input_file: Path,
    output_file: Path | None,
    video_segments: Sequence[str] | Sequence[float],
    odd_args: None | dict[str, str],  # For segments
    even_args: None | dict[str, str] = None,  # For other segments
):
    if output_file is None:
        output_file = input_file.parent / (
            input_file.stem + "_" + _methods.KEEP_OR_REMOVE + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )
    logger.info(f"{_methods.KEEP_OR_REMOVE} {input_file.name} to {output_file.name}")

    # Step 1:convert video segments if needed and double them
    video_segments = deque(
        _convert_seconds_to_timestamp(s) if isinstance(s, (float, int)) else s
        for o in video_segments
        for s in (o, o)
    )  # type: ignore

    # Step 2: create a full segment list
    video_segments.appendleft("00:00:00.000")  # type: ignore
    video_segments.append(_convert_seconds_to_timestamp(probe_duration(input_file)))  # type: ignore

    # Use ThreadPoolExecutor to manage the threads
    temp_dir: Path = Path(tempfile.mkdtemp())
    num_cores = os.cpu_count()
    cut_videos = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cores) as executor:
        futures = []
        for i in range(0, len(video_segments), 2):
            if even_args is None and i % 4 == 0:
                continue
            if odd_args is None and i % 4 == 2:
                continue
            start_time: str = video_segments[i]  # type:ignore
            end_time: str = video_segments[i + 1]  # type:ignore
            if start_time[:8] == end_time[:8]:
                continue
            seg_output_file = temp_dir / f"{i}{input_file.suffix}"
            cut_videos.append(seg_output_file)

            # Submit the cut task to the executor
            future = executor.submit(
                cut, input_file, seg_output_file, start_time, end_time
            )
            futures.append(future)  # Store the future for tracking
            future.result()  # Ensures `cut` completes before proceeding

            further_args = even_args if i % 4 == 0 else odd_args

            if not further_args:
                continue

            # Create full args for further editing
            temp_seg = seg_output_file.parent / (
                seg_output_file.stem + "_temp_seg" + seg_output_file.suffix
            )
            full_args = _create_full_args(
                input_file=seg_output_file,
                output_file=temp_seg,
                **further_args,  # type:ignore
            )

            future = executor.submit(_ffmpeg, **full_args)
            futures.append(future)  # Store the future for tracking
            future.result()  # Ensures `cut` completes before proceeding
            temp_seg.replace(seg_output_file)

        # Optionally, wait for all futures to complete
        # concurrent.futures.wait(futures)

    # Step 4: Sort the cut video paths by filename (index order)
    cut_videos.sort(key=lambda video_file: int(video_file.stem))

    # Step 5: Create input.txt for FFmpeg concatenation
    input_txt_path: Path = temp_dir / "input.txt"
    with open(input_txt_path, "w") as f:
        for video_path in cut_videos:
            f.write(f"file '{video_path}'\n")

    # Step 4: Merge the kept segments
    try:
        merge(input_txt_path, temp_output_file)
        temp_output_file.replace(output_file)
        # Step 5: Clean up temporary files
        for video_path in cut_videos:
            os.remove(video_path)
        # os.remove(input_txt_path)
        # os.rmdir(temp_dir)
    except Exception as e:
        logger.error(
            f"Failed to {_methods.KEEP_OR_REMOVE} for {input_file}. Error: {e}"
        )
        return 1
    return 0


def cut_silence(
    input_file: Path,
    output_file: Path | None = None,
    dB: int = -35,
    sl_duration: float = 0.2,
    seg_min_duration: float = 0,
    odd_args: dict[str, str] | None = None,
    even_args: dict[str, str] | None = None,
) -> int | Enum:
    class error_code(Enum):
        DURATION_LESS_THAN_ZERO = auto()
        NO_VALID_SEGMENTS = auto()
        FAILED_TO_CUT = auto()

    if sl_duration <= 0:
        logger.error(f"Duration must be greater than 0.")
        return error_code.DURATION_LESS_THAN_ZERO

    if odd_args is None:
        odd_args = {}

    if output_file is None:
        output_file = input_file.parent / (
            input_file.stem + "_" + _methods.CUT_SILENCE + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )
    logger.info(
        f"{_methods.CUT_SILENCE} {input_file} to {output_file} with {dB = } ,{sl_duration = }, {seg_min_duration = }."
    )

    non_silence_segments: Sequence[float]
    total_duration: float
    non_silence_segments, total_duration, _ = probe_non_silence(
        input_file, dB, sl_duration
    )

    adjusted_segments: Sequence[float] = _adjust_segments_to_keyframes(
        _ensure_minimum_segment_length(
            non_silence_segments, seg_min_duration, total_duration
        ),
        _probe_keyframe(input_file),
    )

    merged_overlapping_segments: Sequence[float] = _merge_overlapping_segments(
        adjusted_segments
    )
    if merged_overlapping_segments == []:
        logger.error(f"No valid segments found for {input_file}.")
        return error_code.NO_VALID_SEGMENTS

    try:
        advanced_keep_or_remove_by_cuts(
            input_file=input_file,
            output_file=temp_output_file,
            video_segments=merged_overlapping_segments,
            odd_args=odd_args,
            even_args=even_args,
        )
        temp_output_file.replace(output_file)

    except Exception as e:
        logger.error(f"Failed to cut silence for {input_file}. Error: {e}")
        return error_code.FAILED_TO_CUT
    return 0


def _create_cut_sl_filter_tempfile(
    filter_info: Sequence[str],
    videoSectionTimings: Sequence[float],
) -> Path:
    with tempfile.NamedTemporaryFile(
        delete=False, mode="w", encoding="UTF-8", prefix=filter_info[2]
    ) as temp_file:
        for line in _gen_filter(filter_info, videoSectionTimings):
            temp_file.write(f"{line}\n")
        path: Path = Path(temp_file.name)
    return path


def cut_silence_rerender(  # command
    input_file: Path,
    output_file: Path | None = None,
    dB: int = -30,
    sl_duration: float = 0.2,
    **othertags: EncodeKwargs,
) -> int:
    if sl_duration <= 0:
        logger.error(f"Duration must be greater than 0.")
        return 1

    if output_file is None:
        output_file = input_file.parent / (
            input_file.stem + "_" + _methods.CUT_SILENCE + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )
    logger.info(
        f"{_methods.CUT_SILENCE} {input_file} to {output_file} with {dB = } ,{sl_duration = } and {othertags = }"
    )

    non_silence_segments: Sequence[float] = probe_non_silence(
        input_file, dB, sl_duration
    )[0]

    class CSFiltersInfo(Enum):
        VIDEO = [
            "select='",
            "', setpts=N/FRAME_RATE/TB",
            f"temp_{time.strftime("%Y%m%d-%H%M%S")}_video_filter_",
        ]
        AUDIO = [
            "aselect='",
            "', asetpts=N/SR/TB",
            f"temp_{time.strftime("%Y%m%d-%H%M%S")}_audio_filter_",
        ]

    video_filter_script: Path = _create_cut_sl_filter_tempfile(
        CSFiltersInfo.VIDEO.value, non_silence_segments
    )
    audio_filter_script: Path = _create_cut_sl_filter_tempfile(
        CSFiltersInfo.AUDIO.value, non_silence_segments
    )

    output_kwargs: dict = (
        {
            "i": f'"{input_file}"',
            "filter_script:v": video_filter_script,
            "filter_script:a": audio_filter_script,
        }
        | othertags
        | {"y": f'"{temp_output_file}"'}
    )
    logger.info(
        f"{_methods.CUT} {input_file.name} to {output_file.name} with {output_kwargs = }"
    )
    try:
        command: str = f"ffmpeg {_dic_to_ffmpeg_args(output_kwargs)}"
        os.system(command)
        os.remove(video_filter_script)
        os.remove(audio_filter_script)
        temp_output_file.replace(output_file)
    except Exception as e:
        logger.error(f"Failed to cut silence for {input_file}. Error: {e}")
        return 2
    return 0


def _split_segments(  # command
    input_file: Path,
    video_segments: Sequence[float],
    output_dir: Path | None = None,
    **othertags,
) -> Sequence[Path]:
    """
    Cuts the input video into segments based on the provided start and end times.
    """
    if output_dir is None:
        output_dir = input_file.parent / f"{input_file.stem}_segments"

    # Step 2: Use ffmpeg to cut the video into segments
    output_kwargs: dict = (
        {
            "i": f'"{input_file}"',
            "c:v": "copy",
            "c:a": "copy",
            "f": "segment",
            "segment_times": ",".join(map(str, video_segments)),
            "segment_format": input_file.suffix.lstrip("."),
            "reset_timestamps": "1",
        }
        | othertags
        | {"y": f'"{output_dir}/%d_{input_file.stem}{input_file.suffix}"'}
    )
    logger.info(f"Split {input_file.name} to {output_dir} with {output_kwargs = }")
    try:
        # Execute the FFmpeg command
        _ffmpeg(**output_kwargs)
    except Exception as e:
        logger.error(f"Failed to cut videos for {input_file}. Error: {e}")
        raise e

    # Step 3: Collect the cut video segments
    cut_videos: list[Path] = sorted(
        output_dir.glob(f"*{input_file.suffix}"),
        key=lambda video_file: int(video_file.stem.split("_")[0]),
    )

    return cut_videos


def keep_or_remove_by_split_segs(
    input_file: Path,
    output_file: Path | None,
    video_segments: Sequence[str] | Sequence[float],
    keep_handle: bool = True,  # True means keep, False means remove
) -> int:
    """remove a segment from a video

    Raises:
        e: _description_

    Returns:
        _type_: _description_
    """
    if output_file is None:
        output_file = input_file.parent / (
            input_file.stem + "_" + _methods.KEEP_OR_REMOVE + input_file.suffix
        )
    temp_output_file: Path = output_file.parent / (
        output_file.stem + "_processing" + output_file.suffix
    )
    logger.info(f"{_methods.KEEP_OR_REMOVE} {input_file.name} to {output_file.name}")

    # Step 0: Create a temporary folder for storing cut videos
    temp_dir: Path = Path(tempfile.mkdtemp())

    # Step 1: Cut the video into segments based on the provided start and end times
    cut_videos: Sequence[Path] = _split_segments(
        input_file,
        [
            _convert_timestamp_to_seconds(s) if isinstance(s, str) else s
            for s in video_segments
        ],
        temp_dir,
    )

    # Step 2: Sort the cut videos into two lists(0 and 1) based on index % 2
    cut_videos_dict: dict[int, list[Path]] = {}
    for index, path in enumerate(cut_videos):
        cut_videos_dict.setdefault(index % 2, []).append(path)

    # Step 3: Decide which segments to keep and which to remove
    keep_key: int = int(keep_handle)
    remove_key: int = abs(1 - keep_key)

    # Step 4: Remove the unwanted segments
    for video_path in cut_videos_dict[remove_key]:
        os.remove(video_path)

    # Step 5: Create input.txt for FFmpeg concatenation
    temp_dir = cut_videos[0].parent
    input_txt_path: Path = temp_dir / "input.txt"
    with open(input_txt_path, "w") as f:
        for video_path in cut_videos_dict[keep_key]:
            f.write(f"file '{video_path}'\n")

    # Step 6: Merge the kept segments
    try:
        merge(input_txt_path, temp_output_file)
        temp_output_file.replace(output_file)
        # Step 7: Clean up temporary files
        for video_path in cut_videos_dict[keep_key]:
            os.remove(video_path)
        os.remove(input_txt_path)
        os.rmdir(temp_dir)
    except Exception as e:
        logger.error(f"Failed to cut silence for {input_file}. Error: {e}")
        return 1
    return 0
