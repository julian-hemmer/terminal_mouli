#!/usr/bin/python3

import browser_cookie3
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

def start_driver():
    chrome_options = Options()
    chrome_options.add_argument("--disable-webrtc")
    chrome_options.add_argument("--disable-media-stream")
    chrome_options.add_argument("--disable-rtc-smoothness-algorithm")
    chrome_options.add_argument("--disable-rtc-privacy-protections")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--headless=new")
    prefs = {
        "profile.default_content_setting_values.geolocation": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.media_stream": 2,
        "profile.default_content_setting_values.media_stream_mic": 2,
        "profile.default_content_setting_values.media_stream_camera": 2,
        "profile.default_content_setting_values.automatic_downloads": 2,
        "profile.default_content_setting_values.popups": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return (driver)

def get_local_storage_item(driver, key):
    return driver.execute_script(f"return window.localStorage.getItem('{key}');")

def get_token():
    connextion_url="https://login.microsoftonline.com/common/oauth2/authorize?client_id=c3728513-e7f6-497b-b319-619aa86f5b50&nonce=28d21af4-1b1e-403b-8830-ff270cc05ddb&redirect_uri=https%3A%2F%2Fmy.epitech.eu%2Findex.html&response_type=id_token&state=fragment%3Dy%252F2024"
    cookiejar = browser_cookie3.firefox(domain_name='microsoftonline.com')
    driver = start_driver()
    driver.get(connextion_url)

    for cookie in cookiejar:
        cookie_dict = {'name': cookie.name, 'value': cookie.value}
        if cookie.domain:
            cookie_dict['domain'] = cookie.domain
        if cookie.expires:
            cookie_dict['expiry'] = cookie.expires
        if cookie.path_specified:
            cookie_dict['path'] = cookie.path
        driver.add_cookie(cookie_dict)

    driver.refresh()

    value = get_local_storage_item(driver, 'argos-api.oidc-token')
    if value:
        value = value.replace("\"", "")
    else:
        value = ""
    driver.close()
    return value
    