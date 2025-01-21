from modules.bin import *
from pathlib import Path


dic_my_uc_driver_config = {
    CsBasicComponent: None,
    CsMyDriverComponent: None,
    uc.Chrome: None,
    CsMyUCDriveWithUserAgentAndGetResponseInit: {"all_args": True, "all_kwargs": True},
}
CsUCdriver = cs_factory(dic_my_uc_driver_config)


class CsMyUCGooglePhotoUploader:
    def __init__(self):
        self.driver = None
        app_name = "mideoToGPhoto"
        # Define the path to the Roaming folder for the app
        self.app_folder = Path.home() / "AppData" / "Roaming" / "mideoToGPhoto"
        # Create the directory if it doesn't already exist
        self.app_folder.mkdir(parents=True, exist_ok=True)
        self.config_file = self.app_folder / "config.json"
        self.load_config()

    def _start_driver(self, bool_headless=False):
        user_data_dir = self.app_folder / "userProfile"
        self.driver = CsUCdriver(bool_headless, user_data_dir)

        self.driver.maximize_window()
        # List to store each response

    def login(self):
        if not self.driver:
            self._start_driver(False)
        login_url = "https://photos.google.com/login"
        self.driver.get(login_url)
        _wait = self.driver._wait_element(
            By.XPATH, '//input[@type="text"]', condition=EC.element_to_be_clickable
        )

    def load_config(self):
        # Load the config data if the file exists
        if self.config_file.exists():
            with self.config_file.open("r") as file:
                self.config_data = json.load(file)
            print("Configuration loaded:", self.config_data)
        else:
            print("Configuration file not found, Please register first.")
            self.register_config()

    def register_config(self):
        self.config_data = {
            "mideo_folder": input("please input mideo folder:"),
            "album_url": input("please input album url"),
        }

        # Write the config data as JSON
        with self.config_file.open("w") as file:
            json.dump(self.config_data, file, indent=4)

        print(f"Configuration saved to: {self.config_file}")

    def handler(self) -> None:
        pass

    def upload_to_google_photo(self, bool_headless=False) -> str:
        if not self.driver:
            self._start_driver(bool_headless)
        res = self.driver._get_response(self.config_data["album_url"])

        if res["status"] == 404 and bool_headless:
            self.driver.quit()
            self.driver = None
            self.login()
            self.driver.get(self.config_data["album_url"])
        elif res["status"] == 404:
            self.login()
            self.driver.get(self.config_data["album_url"])

        # Locate the input element by aria-label using XPath
        _add_photo_click = self.driver._wait_element(
            By.XPATH, '//button[@aria-label="新增相片"]'
        ).click()
        print("新增相片")
        # Interact with the input element
        _upload_click = self.driver._wait_element(
            By.XPATH, '//span[text()="從電腦中選取"]'
        ).click()
        print("從電腦中選取")
        file_input = self.driver.find_element(By.XPATH, '//input[@type="file"]')
        files_path = self._list_mkv_files(self.config_data["mideo_folder"])
        file_input.send_keys(files_path)
        self.driver._wait_element(By.XPATH, f"//div[contains(text(), '你已備份')]")
        print("Upload successfully")
        self.driver.quit()
        self.driver = None

    def _list_mkv_files(self, mideo_folder) -> str:
        # Get all .mkv files in the folder
        mkv_files = [
            mideo_folder + "\\" + file
            for file in os.listdir(mideo_folder)
            if file.endswith(".mkv")
        ]
        # Join the list of files into a single string separated by newline characters
        mkv_files_str = "\n".join(mkv_files)
        return mkv_files_str


dic_uploader_config = {CsBasicComponent: None, CsMyUCGooglePhotoUploader: {}}
