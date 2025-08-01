from kiteconnect import KiteConnect
import sqlite3
from langchain_groq import ChatGroq
from selenium import webdriver
from selenium.webdriver.common.by import By
from pyotp import TOTP
import time


def create_sqlite_connection(db_path: str):
    """Create a SQLite database connection."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    return conn, cursor


def init_chat_model(api_key: str):

    llm = ChatGroq(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        api_key=api_key,
    )
    return llm


def autologin_zerodha(key_secret):
    # token_path = "api_key.txt"
    # key_secret = open(token_path,'r').read().split()
    kite = KiteConnect(api_key=key_secret[0])
    service = webdriver.chrome.service.Service("./chromedriver")
    service.start()
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    # options = options.to_capabilities()
    driver = webdriver.Remote(service.service_url, options=options)
    driver.get(kite.login_url())
    driver.implicitly_wait(10)
    username = driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[1]/input"
    )
    password = driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/input"
    )
    username.send_keys(key_secret[2])
    password.send_keys(key_secret[3])
    driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[4]/button",
    ).click()
    pin = driver.find_element(
        By.XPATH, "/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div/input"
    )
    pin.click()
    pin.clear()
    totp = TOTP(key_secret[4])
    token = totp.now()
    pin.send_keys(token)
    driver.implicitly_wait(10)

    # pin.send_keys(key_secret[4])
    driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div[2]/div[1]/div/div/div[2]/form/div[2]/button",
    ).click()
    time.sleep(1)
    request_token = driver.current_url.split("request_token=")[1][:32]
    with open("request_token.txt", "w") as the_file:
        the_file.write(request_token)
    driver.quit()
    request_token = open("request_token.txt", "r").read()
    # key_secret = open("api_key.txt",'r').read().split()
    kite = KiteConnect(api_key=key_secret[0])
    data = kite.generate_session(request_token, api_secret=key_secret[1])
    # with open('access_token.txt', 'w') as file:
    #     file.write(data["access_token"])
    print("Auto login Completed")
    return data["access_token"]
