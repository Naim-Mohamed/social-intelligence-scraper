import os
import sys
from pathlib import Path

from dotenv import load_dotenv


class Passwords:
    """Centralized environment-backed settings for credentials and database config."""

    EXPECTED_KEYS = (
        "TWITTER_USERNAME",
        "TWITTER_PASSWORD",
        "TWITTER_LOGIN",
        "TWITTER_EMAIL",
        "TWITTER_PHONE",
        "INSTAGRAM_USERNAME",
        "INSTAGRAM_PASSWORD",
        "LINKEDIN_USERNAME",
        "LINKEDIN_PASSWORD",
        "OPENAI_API_KEY",
        "DB_HOST",
        "DB_USER",
        "DB_PASS",
        "DB_NAME",
        "TWITTER_USER",
        "TWITTER_PASS",
        "INSTA_USER",
        "INSTA_PASS",
        "LINKED_USER",
        "LINKED_PASS",
        "LINKEDIN_USER",
        "LINKEDIN_PASS",
        "AI_API_KEY",
    )

    def __init__(self):
        self.env_path = None
        self._load_env_file()
        self.data_map = {}
        self._populate_data()

    def _load_env_file(self):
        project_root = Path(__file__).resolve().parents[1]
        candidate_paths = (
            project_root / ".env",
            project_root.parent / ".env",
        )

        for env_path in candidate_paths:
            if env_path.exists():
                load_dotenv(env_path)
                self.env_path = env_path
                return

        checked_paths = ", ".join(str(path) for path in candidate_paths)
        print("ERROR: .env file was not found.")
        print(f"Checked: {checked_paths}")
        sys.exit(1)

    def _populate_data(self):
        for key in self.EXPECTED_KEYS:
            value = os.getenv(key)
            if value is None and key in self._primary_keys():
                print(f"Warning: environment variable [{key}] is missing.")
            self.data_map[key] = value

    def _primary_keys(self):
        return {
            "DB_HOST",
            "DB_USER",
            "DB_PASS",
            "DB_NAME",
        }

    def get_credential(self, platform, key_type):
        platform_aliases = {
            "twitter": ("TWITTER",),
            "insta": ("INSTAGRAM", "INSTA"),
            "instagram": ("INSTAGRAM", "INSTA"),
            "linked": ("LINKEDIN", "LINKED"),
            "linkedin": ("LINKEDIN", "LINKED"),
        }
        key_aliases = {
            "user": ("USERNAME", "USER"),
            "username": ("USERNAME", "USER"),
            "pass": ("PASSWORD", "PASS"),
            "password": ("PASSWORD", "PASS"),
        }

        platform_keys = platform_aliases.get(platform.lower(), (platform.upper(),))
        credential_keys = key_aliases.get(key_type.lower(), (key_type.upper(),))

        for platform_key in platform_keys:
            for credential_key in credential_keys:
                value = self.data_map.get(f"{platform_key}_{credential_key}")
                if value:
                    return value

        return None

    def get_db_config(self):
        return {
            "host": self.data_map.get("DB_HOST"),
            "user": self.data_map.get("DB_USER"),
            "password": self.data_map.get("DB_PASS"),
            "database": self.data_map.get("DB_NAME"),
        }

    def get_ai_key(self):
        return self.data_map.get("OPENAI_API_KEY") or self.data_map.get("AI_API_KEY")


if __name__ == "__main__":
    settings = Passwords()
    db = settings.get_db_config()

    print(f"Settings loaded from: {settings.env_path}")
    print(f"Database host configured: {bool(db['host'])}")
    print(f"Database name configured: {bool(db['database'])}")
    print(f"Twitter username configured: {bool(settings.get_credential('twitter', 'user'))}")
    print(f"Instagram username configured: {bool(settings.get_credential('instagram', 'user'))}")
    print(f"LinkedIn username configured: {bool(settings.get_credential('linkedin', 'user'))}")
    print(f"AI key configured: {bool(settings.get_ai_key())}")
