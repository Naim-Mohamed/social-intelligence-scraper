import os
from pathlib import Path
import hashlib
import time

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import Passwords
from src.database.DatabaseGuard import DatabaseGuard
from src.scrapers.Search import Search


class LinkedInScraper:
    MIN_CONTENT_LENGTH = 80
    RESULT_SELECTOR = (
        ".reusable-search__result-container, "
        ".entity-result, "
        "[data-chameleon-result-urn], "
        "[data-view-name='search-entity-result-universal-template'], "
        ".search-results-container li, "
        ".reusable-search__entity-result-list li, "
        ".search-results__list li"
    )

    def __init__(self):
        self.creds = Passwords()
        self.username = self.creds.get_credential("linked", "user")
        self.password = self.creds.get_credential("linked", "pass")
        self.search_engine = Search()
        self.db_guard = DatabaseGuard()

        project_root = Path(__file__).resolve().parents[2]

        selenium_cache = project_root / ".selenium_cache"
        selenium_cache.mkdir(exist_ok=True)
        os.environ["SE_CACHE_PATH"] = str(selenium_cache)

        chrome_profile = project_root / ".chrome_linkedin_profile"
        chrome_profile.mkdir(exist_ok=True)

        options = Options()
        options.add_argument(f"--user-data-dir={chrome_profile}")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        options.add_argument("--remote-debugging-port=0")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

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
        print("Logging in to LinkedIn...")
        self.driver.get("https://www.linkedin.com/login")

        try:
            time.sleep(2)
            if self._is_logged_in():
                print("Already logged in with the current Chrome profile.")
                return True

            username_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            password_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "password"))
            )

            username_field.clear()
            username_field.send_keys(self.username or "")
            password_field.clear()
            password_field.send_keys(self.password or "")
            password_field.send_keys(Keys.ENTER)

            print("Login submitted.")
            time.sleep(5)

            current_url = self.driver.current_url.lower()
            if "login" in current_url or "checkpoint" in current_url:
                print(f"Login was not confirmed. Current page: {self.driver.current_url}")
                return False

            print("Login appears successful.")
            return True
        except TimeoutException:
            if self._is_logged_in():
                print("Already logged in with the current Chrome profile.")
                return True

            print("Login fields were not found before the timeout.")
            print(f"Current page: {self.driver.current_url}")
            print(f"Page title: {self.driver.title}")
            return False
        except Exception as error:
            print(f"Login error: {type(error).__name__}: {error}")
            return False

    def scrape_all_keywords(self, limit_per_keyword=15):
        """Collect only new, database-confirmed results for each keyword."""
        search_urls = self.search_engine.generate_linkedin_urls()
        all_extracted_data = []

        for index, url in enumerate(search_urls, start=1):
            keyword = self.search_engine.keywords[index - 1]
            print(f"Searching keyword ({index}/{len(search_urls)}): {keyword}")

            self.driver.get(url)
            time.sleep(5)

            saved_count = 0
            scanned_urls = set()
            scroll_attempts = 0
            max_scroll_attempts = 8

            while saved_count < limit_per_keyword and scroll_attempts <= max_scroll_attempts:
                results = self.driver.find_elements(By.CSS_SELECTOR, self.RESULT_SELECTOR)
                print(
                    f"Found {len(results)} raw result elements. "
                    f"Saved {saved_count}/{limit_per_keyword} new results."
                )

                for post in results:
                    post_text = post.text.strip()
                    if len(post_text) < self.MIN_CONTENT_LENGTH:
                        continue

                    post_url = self._extract_post_url(post, post_text)
                    normalized_url = self.db_guard.normalize_url(
                        post_url, base_url=self.driver.current_url
                    )
                    if not normalized_url or normalized_url in scanned_urls:
                        continue

                    scanned_urls.add(normalized_url)
                    if self.db_guard.is_duplicate(normalized_url, "linkedin"):
                        print(f"Duplicate skipped: {normalized_url}")
                        continue

                    inserted = self.db_guard.insert_raw(
                        "linkedin", keyword, post_text, normalized_url
                    )
                    if not inserted:
                        print(f"Insert skipped by database guard: {normalized_url}")
                        continue

                    all_extracted_data.append(
                        {
                            "keyword": keyword,
                            "content": post_text,
                            "post_url": normalized_url,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )
                    saved_count += 1
                    print(f"Saved new result {saved_count}/{limit_per_keyword}.")

                    if saved_count >= limit_per_keyword:
                        break

                if saved_count < limit_per_keyword:
                    self._scroll_results_once()
                    scroll_attempts += 1

            print(f"Saved {saved_count} results for {keyword}.")
            time.sleep(3)

        print(f"Task complete. Total collected posts: {len(all_extracted_data)}")
        return all_extracted_data

    def _is_logged_in(self):
        current_url = self.driver.current_url.lower()
        return "linkedin.com/feed" in current_url or "linkedin.com/in/" in current_url

    def _scroll_results(self):
        body = self.driver.find_element(By.TAG_NAME, "body")
        for _ in range(3):
            body.send_keys(Keys.PAGE_DOWN)
            time.sleep(2)

    def _scroll_results_once(self):
        body = self.driver.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(2)

    def _extract_post_url(self, post, post_text):
        anchors = post.find_elements(By.CSS_SELECTOR, "a[href]")
        hrefs = [
            anchor.get_attribute("href")
            for anchor in anchors
            if anchor.get_attribute("href")
        ]

        preferred_markers = (
            "/feed/update/",
            "/posts/",
            "/pulse/",
            "activity-",
            "urn:li:activity",
        )
        for href in hrefs:
            if any(marker in href for marker in preferred_markers):
                return href

        for href in hrefs:
            lowered = href.lower()
            if lowered.startswith("mailto:"):
                continue
            if "linkedin.com" in lowered or "lnkd.in" in lowered:
                continue
            return href

        content_hash = hashlib.sha256(post_text.encode("utf-8")).hexdigest()
        return f"linkedin://search-result/{content_hash}"


if __name__ == "__main__":
    bot = LinkedInScraper()
    try:
        if bot.login():
            data = bot.scrape_all_keywords()
            print(f"Prepared {len(data)} leads for the next stage.")

        time.sleep(10)
    finally:
        bot.driver.quit()
