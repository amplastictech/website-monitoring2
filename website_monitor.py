import smtplib
import os
import time
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Configuration
URL = "https://www.kbdbodykits.com/account.php/orders"
EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
USERNAME = "eggleton"
PASSWORD = os.environ.get('WEBSITE-PASSWORD')

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent successfully")
    except Exception as e:
        print(f"Failed to send email: {e}")

def setup_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("--headless")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0")
    return webdriver.Firefox(options=options)

def login(driver):
    driver.get(URL)
    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = driver.find_element(By.ID, "password")
        login_button = driver.find_element(By.NAME, "login")
        
        username_field.clear()
        username_field.send_keys(USERNAME)
        password_field.clear()
        password_field.send_keys(PASSWORD)
        login_button.click()
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body"))
        )
        return True
    except (TimeoutException, NoSuchElementException) as e:
        print(f"Login failed: {e}")
        return False

def check_website():
    driver = setup_driver()
    try:
        if not login(driver):
            send_email("Website Monitor: Login Failed", 
                      f"Failed to login to {URL}\nTimestamp: {time.ctime()}")
            return

        # Check for 404 error
        if "404" in driver.title.lower() or "not found" in driver.title.lower() or "the page" in driver.page_source.lower():
            send_email("Website Monitor: 404 Error Detected",
                      f"404 error detected on {URL}\nTimestamp: {time.ctime()}\nPage title: {driver.title}")
        else:
            print(f"Check completed successfully at {time.ctime()}")

    except Exception as e:
        send_email("Website Monitor: Error", 
                  f"Error checking website: {str(e)}\nTimestamp: {time.ctime()}")
    finally:
        driver.quit()

if __name__ == "__main__":
    check_website()
