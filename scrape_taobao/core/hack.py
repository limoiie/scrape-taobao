import logging
import os

import rich.prompt
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from scrape_taobao.utils import fake_pause

logger = logging.getLogger(__name__)

STEALTH_JS = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../stealth.min.js")
)


def hide_browser_features(driver: webdriver.Chrome):
    with open(STEALTH_JS) as f:
        script = f.read()

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument", dict(source=script)
    )


def prompt_and_login(driver):
    username = rich.prompt.Prompt.ask("username")
    password = rich.prompt.Prompt.ask("password", password=True)

    login(driver, username, password)
    fake_pause()

    if "login.jhtml" in driver.current_url:
        # still on the login page
        logger.exception('failed to login as "{}"'.format(username))
        exit(-1)

    logger.info('logged in as "{}"'.format(username))


def login(driver: WebDriver, username: str, password: str):
    driver.get("https://login.taobao.com/member/login.jhtml")

    password_login_tab = driver.find_element(
        By.CLASS_NAME, "password-login-tab-item"
    )
    password_login_tab.click()
    fake_pause()

    username_input = driver.find_element(By.ID, "fm-login-id")
    username_input.clear()
    username_input.send_keys(username)
    fake_pause()

    password_input = driver.find_element(By.ID, "fm-login-password")
    password_input.clear()
    password_input.send_keys(password)
    fake_pause()

    submit_button = driver.find_element(By.CLASS_NAME, "fm-submit")
    submit_button.click()
