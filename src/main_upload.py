import os
import asyncio
import pdb
from pathlib import Path
from app import config, tasks, browser_instances, logger  # , GPhoto_uploader
from app.services.my_driver.types import MyDriverConfig


# sample
name = "abc"
browser_config: MyDriverConfig = {
    "user_data_dir": Path(config.AppPaths.APP_DATA) / name,
    "browser_executable_path": Path(
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ),
}

task1: tasks.UploaderTask = {
    "name": "xiaomi",
    "local_album_path": Path(r"D:\smb\xiaomi\xiaomi_camera_videos\94f827b4b94e"),
    "GPhoto_url": "https://photos.google.com/share/AF1QipN5ErAyjjFPCxWgw--uYgbrvJWZu1U39-3iyeChyQQv0PDxU59NnyNP_k4bZNMrvw?key=czBUY1Z4UWRjdDFMWXFYdS1NZnd4SXIyREgzTElR",
    "browser_config": browser_config,
    "delete_after": True,
}
task2: tasks.UploaderTask = {
    "name": "xiaomi_speedup",
    "local_album_path": Path(r"D:\smb\xiaomi\xiaomi_camera_videos\94f827b4b94e")
    / "cut_sl_speedup",
    "GPhoto_url": "https://photos.google.com/share/AF1QipMk6l7y_pzXMh1gTWH5G2lD_U30_Br2E-p2sKDw71YBY97zMh6krVC9cDsT-acFjQ",
    "browser_config": browser_config,
    "delete_after": True,
}

upload_assignments: tasks.UploaderInfo = {
    "filename": Path(),
    "assignments": [task1, task2],
}


async def main():
    assignments = upload_assignments.get("assignments")
    logger.info(f"Start uploading tasks:{assignments}")

    if not assignments:
        logger.info("No assignment")
        return

    for task in assignments:
        folder: Path = task["local_album_path"]
        task["mkv_files"] = mkv_files = [
            folder / file for file in os.listdir(folder) if file.endswith(".mkv")
        ]

        if not mkv_files:
            logger.info(f"No mkv files in {folder}, pass")
            return

        logger.info(f"Start uploading {mkv_files} to {task["GPhoto_url"]}")
        await GPhoto_uploader.upload_handler(task)

    # Clear tabs
    logger.info(f"All tasks done, close all browsers")
    keys = list(browser_instances.keys())
    for key in keys:
        if key in browser_instances:
            browser_instances[key].stop()
            del browser_instances[key]

    # Your script code here
    # print("This is a script in debug mode.")
    # Set a breakpoint
    # pdb.set_trace()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
