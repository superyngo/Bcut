import asyncio
from pathlib import Path
import os
from nodriver import Tab
from ...utils import logger
from ...services import my_driver
from ...models.tasks import UploaderTask


__all__: list[str] = ["upload_handler"]

# # sample
# name = "abc"
# browser_config: MyDriverConfig = {
#     "user_data_dir": Path(config.AppPaths.APP_DATA) / name,
#     "browser_executable_path": Path(
#         r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
#     ),
# }

# task: UploaderTask = {
#     "name": name,
#     "local_album_path": Path(
#         r"D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\文件\Projects\Python\sample\cut_sl_speedup"
#     ),
#     "GPhoto_url": "https://photos.google.com/u/2/album/AF1QipPgIsi5cicSG2EPtPq_fD1mDUtvkTjdr4d16aGe",
#     "browser_config": browser_config,
# }


async def _upload(tab: Tab, mkv_files: list[Path]) -> int:

    # Check all mkv files valid
    for file in mkv_files:
        if file.suffix != ".mkv":
            logger.info(f"{file} is not mkv file")
            return 1

    # Locate the 新增相片 and click
    Add_New = await tab.find("//span[text()='新增相片']", timeout=999)
    if not Add_New:
        logger.info("新增相片 not found")
        return 2
    do = await Add_New.click()
    logger.info("新增相片")

    # Interact with the "Select from Computer" button
    upload_button = await tab.find('//span[text()="從電腦中選取"]')
    if not upload_button:
        logger.info("從電腦中選取 not found")
        return 2
    do_stop_os_dialog = await tab.evaluate(
        """
        document.addEventListener('click', (event) => {
        if (event.target.type === 'file') {
            event.preventDefault(); // Prevent file dialog
            console.log('File dialog prevented');
        }
        });
    """
    )
    do_click = await upload_button.click()
    logger.info("從電腦中選取")

    # Locate the file input element
    file_input = await tab.find('//input[@type="file"]')
    if not file_input:
        logger.info("upload not found")
        return 2
    do = await file_input.send_file(*mkv_files)  # Set files for upload

    # Wait for confirmation message
    await tab.find("你已備份", timeout=999999999)
    logger.info("Upload successfully")
    return 0


def _delete_mkv_files(mkv_files: list[Path]) -> int:
    # Iterate through each .mkv file and delete it
    try:
        for file in mkv_files:
            os.remove(file)
            logger.info(f"Deleted: {file}")
        return 0

    except Exception as e:
        logger.info(f"Error deleting {mkv_files}: {e}")
        return 1


async def upload_handler(task: UploaderTask) -> int:
    """_summary_

    Args:
        task (UploaderTask): _description_

    Returns:
        int: _description_
    """

    browser_config: my_driver.types.MyDriverConfig = task.get("browser_config", {})
    tab: Tab = await my_driver.init_my_driver(browser_config)

    do_get: Tab = await tab.get(task["GPhoto_url"])
    mkv_files: list[Path] = task.get("mkv_files", [Path()])
    do_upload: int = await _upload(tab, mkv_files)
    await tab.wait(5)
    if do_upload != 0:
        logger.info("upload failed with do_upload")
        return do_upload
    do_delete: int = _delete_mkv_files(mkv_files) if task.get("delete_after") else 0
    return do_delete


async def main():
    pass


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
