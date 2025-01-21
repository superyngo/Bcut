# 20241030
from modules.timestamp import *
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException, NoAlertPresentException
import undetected_chromedriver as uc
import hashlib
import requests
import json

os.environ['HTTPS_PROXY'] = ''
os.environ['HTTP_PROXY'] = ''

def fn_log(str_log:str, str_filename:str = "") -> None:
    # Get the current date and time
    current_time = datetime.datetime.now()
    # Format the timestamp as a readable string
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    # Define the log message with the timestamp
    log_message = f"{timestamp} - {str_log}\n"
    # Open the log file in append mode ('a')
    if str_filename == "":
        str_filename = f"{STR_DATESTAMP}_log.txt"
    with open(f"{STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH}\\{str_filename}", 'a') as log_file:
        # Write the log message to the file
        log_file.write(log_message)
    print(log_message)

def create_sha256_hash(data):
    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()
    
    # Encode the input data to bytes (if it's a string) and update the hash object
    sha256_hash.update(data.encode('utf-8'))
    
    # Get the hexadecimal representation of the hash
    return sha256_hash.hexdigest()

class CsBasicComponent:
    def __getattr__(self, name):
        raise AttributeError(f"'{self.__class__.__name__}' '{name}' was not set")

class CsMyDriverComponent:
    def _select_change_value(self, By_locator: str, locator: str, new_value: str) -> None:
        _select_element = WebDriverWait(self, 20).until(EC.element_to_be_clickable((By_locator, locator)))
        _select_element = Select(_select_element)  # Create a Select instance
        _select_element.select_by_value(new_value)
    def _input_send_keys(self, By_locator: str, locator: str, new_value: str) -> None:
        _input_element = WebDriverWait(self, 20).until(EC.element_to_be_clickable((By_locator, locator)))
        _input_element.clear()
        _input_element.send_keys(new_value)
    def _wait_element(self, By_locator: str, locator: str, time: int = 1000, condition=EC.presence_of_element_located):
        try:
            return WebDriverWait(self, time).until(condition((By_locator, locator)))
        except UnexpectedAlertPresentException:
            try:
                self.switch_to.alert.accept()
            except NoAlertPresentException:
                pass
        return WebDriverWait(self, time).until(condition((By_locator, locator)))
    def _try_extract_element_value(self, element, error_return = "") -> str:
        try:
            match element.tag_name:
                case 'input' | 'textarea':
                    if element.get_attribute('type') == 'checkbox':
                        return element.get_attribute('checked')
                    return element.get_attribute('value')
                case 'select':
                    return Select(element).first_selected_option.text
                case _:
                    return element.text
        except NoSuchElementException:
            return error_return

class CsMyUCDriveWithUserAgentAndGetResponseInit:
    def __init__(self, bool_headless=False, user_data_dir=None):
        self.responses = []
        options = uc.ChromeOptions()
        options.unhandled_prompt_behavior = 'accept'
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if bool_headless:
            options.add_argument('--headless')  # Enable headless mode
            options.add_argument('--disable-gpu')  # Disable GPU rendering
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")

        # user agent
        latest_user_agent = requests.get('http://headers.scrapeops.io/v1/user-agents?api_key=5f0dd055-a569-430e-a964-e49d53548856').json()
        options.add_argument(f"--user-agent={latest_user_agent['result'][0]}")
        
        # Enable Chrome DevTools Protocol
        # https://developer.chrome.com/docs/chromedriver/logging/performance-log
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}

        config = {
            'desired_capabilities': caps,
            'options': options,
            'use_subprocess': False
        } | {'user_data_dir': user_data_dir} if user_data_dir else {}
        
        super(type(self),self).__init__(**config)

    def _get_response(self, url):
        self.get(url)
        # Parse the Chrome Performance logs
        response = None
        for log_entry in self.get_log("performance"):
            log_message = json.loads(log_entry["message"])["message"]
            # Filter out HTTP responses
            if log_message["method"] == "Network.responseReceived":
                self.responses.append(log_message["params"]["response"])
                if log_message["params"]["type"] == "Document":
                    response = log_message["params"]["response"]
        return response

def cs_factory(dic_cs: dict):
    bases = tuple(dic_cs.keys())
    slots = {slot for base in bases if hasattr(base, '__slots__') for slot in getattr(base, '__slots__')}

    # Define the dynamic class with type
    def init(self, *args, **kwargs):
        # config = {'default_args': [],'all_args': bool,'default_kwargs': {},'all_kwargs': bool}
        for Cs, config in dic_cs.items():
            if config is None:
                continue
            _args = config.get('default_args', []) + [*args] if config.get('all_args', False) else []
            _kwargs = config.get('default_kwargs', {}) | kwargs if config.get('all_kwargs', False) else {key: kwargs.get(key, value) for key, value in config.get('default_kwargs', {}).items()}

            Cs.__init__(self, *_args, **_kwargs)

    # Create the class with type
    return type('_Cs', bases, {'__slots__': slots, '__init__': init})



