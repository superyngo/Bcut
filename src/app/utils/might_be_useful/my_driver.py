# 20241014
from .multithreading import *
from .common import *
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException, TimeoutException, NoAlertPresentException, JavascriptException
from typing import Self

class CsMyDriverComponent: 
    def _select_change_value(self:Self, By_locator: str, locator: str, new_value: str) -> None:
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
    def _try_wait_extract_element_value(self, By_locator: str, locator: str, error_return = "") -> str:
        try:
            element = self.find_element(By_locator, locator)
            return self._try_extract_element_value(element)
        except NoSuchElementException:
            return error_return
class CsMyEdgeDriverInit:
    def __init__(self, user_data_dir):
        import logging
        Service = webdriver.EdgeService
        Options = webdriver.EdgeOptions
        # Suppress selenium and webdriver_manager logs
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
        # Set up paths
        user_data_dir = os.path.abspath(user_data_dir)
        log_path = os.path.abspath("./logs/edge_driver.log")

        # Create directories if they don't exist
        os.makedirs(user_data_dir, exist_ok=True)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        edge_bin = './app/bin/msedgedriver.exe'
        service_args=[
                    #   '--log-level=ALL',
                    #   '--append-log',
                    #   '--readable-timestamp',
                    '--disable-build-check',
                    ]
        service = Service(executable_path=edge_bin, service_args=service_args)
        options = Options()
        options.unhandled_prompt_behavior = 'accept'
        options.add_argument('--inprivate')
        # options.add_argument(f"user-data-dir={user_data_dir}")
        options.add_argument("--disable-notifications")
        options.add_argument("--log-level=3")
        super(type(self),self).__init__(service=service, options=options)
        self.int_main_window_handle = self.current_window_handle

