import os
from pathlib import Path
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import Passwords


class TwitterScraper:
    def __init__(self):
        self.creds = Passwords()
        self.username = self.creds.get_credential("twitter", "user")
        self.password = self.creds.get_credential("twitter", "pass")
        self.login_identifier = (
            os.getenv("TWITTER_LOGIN")
            or os.getenv("TWITTER_EMAIL")
            or os.getenv("TWITTER_PHONE")
            or self.username
        )

        if not self.login_identifier or not self.password:
            raise ValueError("Twitter credentials are missing from .env.")

        project_root = Path(__file__).resolve().parents[2]

        selenium_cache = project_root / ".selenium_cache"
        selenium_cache.mkdir(exist_ok=True)
        os.environ["SE_CACHE_PATH"] = str(selenium_cache)

        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        chrome_path = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
        if chrome_path.exists():
            options.binary_location = str(chrome_path)

        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                """
            },
        )

        self.wait = WebDriverWait(self.driver, 20)

    def login(self):
        print("Opening x.com...")
        self.driver.get("https://x.com/")

        try:
            login_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//a[@data-testid='loginButton'] "
                        "| //a[.//span[contains(text(), 'Sign in')]] "
                        "| //a[contains(., 'Sign in')] "
                        "| //span[contains(text(), 'Log in')] "
                        "| //span[contains(text(), 'تسجيل الدخول')]",
                    )
                )
            )
            login_btn.click()
            time.sleep(2)

            print("Typing username...")
            user_field = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@autocomplete='username'] | //input[@name='text']")
                )
            )
            user_field.send_keys(self.login_identifier)
            user_field.send_keys(Keys.ENTER)
            time.sleep(3)

            if self.driver.find_elements(By.XPATH, "//button//span[text()='Next']"):
                print("Clicking Next...")
                next_button = self.wait.until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button//span[text()='Next'] "
                            "| //button//span[text()='التالي'] "
                            "| //button//span[text()='Sign in'] "
                            "| //button//span[text()='Log in']",
                        )
                    )
                )
                next_button.click()
                time.sleep(3)

            body_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            verification_fields = self.driver.find_elements(
                By.CSS_SELECTOR,
                "input[data-testid='ocfEnterTextTextInput'], input[name='text']",
            )
            needs_verification = (
                "enter your phone number or email address" in body_text
                or "enter your phone number or username" in body_text
                or "verify" in body_text
            )
            if (
                needs_verification
                and verification_fields
                and not self.driver.find_elements(By.NAME, "password")
            ):
                print("Completing extra username verification step...")
                verification_fields[0].clear()
                verification_value = (
                    os.getenv("TWITTER_EMAIL")
                    or os.getenv("TWITTER_PHONE")
                    or self.login_identifier
                )
                verification_fields[0].send_keys(verification_value)
                verification_fields[0].send_keys(Keys.ENTER)
                time.sleep(3)

            print("Typing password...")
            pass_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "password"))
            )
            pass_field.send_keys(self.password)
            pass_field.send_keys(Keys.ENTER)

            print("Password submitted.")
            time.sleep(5)

            current_url = self.driver.current_url.lower()
            if "login" in current_url or "flow/login" in current_url:
                print(f"Login was not confirmed. Current page: {self.driver.current_url}")
                return False

            print("Login appears successful.")
            return True
        except Exception as error:
            print(f"Twitter login stopped: {type(error).__name__}: {error}")
            return False


if __name__ == "__main__":
    bot = TwitterScraper()
    try:
        bot.login()
    finally:
        bot.driver.quit()
