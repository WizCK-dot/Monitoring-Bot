from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

import json

with open('settings.json', 'r') as file:
    settings = json.load(file)

EMAIL = settings['email']
PASSWORD = settings['password']

def process_page(target_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://creators.joinmavely.com/auth/login")
        
        wait = WebDriverWait(driver, 10)
        current_url = driver.current_url
        time.sleep(5)

        if "auth" in current_url:
            print("Login page detected, logging in...")
            login(driver, wait)
            time.sleep(3)
            extracted_url = input_url(driver, wait, target_url)
        elif "home" in current_url:
            print("Already on the homepage, inputting URL...")
            extracted_url = input_url(driver, wait, target_url)
        else:
            print(f"Unexpected URL detected: {current_url}")
            extracted_url = None
    
        return extracted_url

    finally:
        driver.quit()

def login(driver, wait):
    print("Performing login...")
    try:
        email_input = wait.until(EC.presence_of_element_located((By.NAME, "email")))
        email_input.send_keys(EMAIL)

        password_input = driver.find_element(By.NAME, "password")
        password_input.send_keys(PASSWORD)

        login_button = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        login_button.click()

        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Enter URL to create a link"]')))
        print("Logged in and navigated to homepage successfully!")
    except Exception as e:
        print(f"Error during login: {e}")

def input_url(driver, wait, target_url):
    print("Inputting URL...")
    try:
        url_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Enter URL to create a link"]')))

        if url_input:
            url_input.send_keys(target_url)
            submit_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
            submit_button.click()
            wait.until(EC.presence_of_element_located((By.ID, 'headlessui-portal-root')))
            print("URL submitted successfully!")
            print("Extracting content...")
            return extract_links(driver, wait)
        else:
            print("Failed to find the input URL element.")
            return None

    except Exception as e:
        print(f"Error while inputting URL: {e}")
        return None

def extract_links(driver, wait):
    try:
        portal_root = wait.until(EC.presence_of_element_located((By.ID, "headlessui-portal-root")))
        paragraphs = portal_root.find_elements(By.TAG_NAME, "p")

        for paragraph in paragraphs:
            text_content = paragraph.text
            urls = re.findall(r'https?://[^\s]+', text_content)
            if urls:
                for url in urls:
                    return url
            else:
                print("No link or URL found in this paragraph.")
        return None
    except Exception as e:
        print(f"Error while extracting links: {e}")
        return None    
