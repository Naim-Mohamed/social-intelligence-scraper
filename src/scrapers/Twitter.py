import os
from pathlib import Path
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config.settings import Passwords

class TwitterScraper:
    def __init__(self):
        self.creds = Passwords()
        self.username = self.creds.get_credential("twitter", "user")
        self.password = self.creds.get_credential("twitter", "pass")

        project_root = Path(__file__).resolve().parents[2]

        selenium_cache = project_root / ".selenium_cache"
        selenium_cache.mkdir(exist_ok=True)
        os.environ["SE_CACHE_PATH"] = str(selenium_cache)

        options = Options()
        
        # 1. إخفاء خاصية الـ WebDriver تماماً
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        # 2. إضافة "بصمة إصبع" لمتصفح حقيقي (User-Agent)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        chrome_path = Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
        if chrome_path.exists():
            options.binary_location = str(chrome_path)

        self.driver = webdriver.Chrome(options=options)

        # 3. كسر الـ WebDriver flag برمجياً (الضربة القاضية للكشف)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        
        self.wait = WebDriverWait(self.driver, 20)

    def login(self):
        print("🏠 التوجه إلى الصفحة الرئيسية x.com...")
        self.driver.get("https://x.com/")
        
        try:
            # 1. الضغط على زر تسجيل الدخول الرئيسي
            login_btn = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//a[@data-testid='loginButton'] | //span[contains(text(), 'Log in')] | //span[contains(text(), 'تسجيل الدخول')]"
            )))
            login_btn.click()
            time.sleep(2)

            # 2. كتابة اسم المستخدم
            print(f"✍️ كتابة اليوزر: {self.username}")
            user_field = self.wait.until(EC.presence_of_element_located(
                (By.XPATH, "//input[@autocomplete='username'] | //input[@name='text']")
            ))
            time.sleep(1)
            user_field.send_keys(self.username)
            
            # 3. الضغط على زر Next
            print("🖱️ الضغط على زر Next...")
            next_button = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//button//span[text()='Next'] | //button//span[text()='التالي']"
            )))
            time.sleep(1)
            next_button.click()
            
            time.sleep(3)

            # 4. كتابة كلمة السر
            print("🔑 كتابة كلمة السر...")
            pass_field = self.wait.until(EC.presence_of_element_located((By.NAME, "password")))
            time.sleep(1)
            pass_field.send_keys(self.password)
            
            # 5. الضغط على زر تسجيل الدخول النهائي
            print("🚀 الضغط على زر Log in النهائي...")
            final_login = self.wait.until(EC.element_to_be_clickable((
                By.XPATH, "//button[@data-testid='LoginForm_Login_Button'] | //span[text()='Log in'] | //span[text()='تسجيل الدخول']"
            )))
            time.sleep(2)
            final_login.click()

            print("🎉 تم الدخول إلى الحساب بنجاح!")

        except Exception as e:
            print(f"⚠️ حدث توقف: {e}")

if __name__ == "__main__":
    bot = TwitterScraper()
    try:
        bot.login()
        print("👀 المتصفح سيبقى مفتوحاً لـ 20 ثانية لتفحص النتيجة...")
        time.sleep(50)
    finally:
        bot.driver.quit()
