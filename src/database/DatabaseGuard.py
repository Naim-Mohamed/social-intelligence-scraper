from contextlib import contextmanager
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse

import pymysql
from pymysql.err import IntegrityError

from config.settings import Passwords


class DatabaseGuard:
    TRACKING_PARAMS = {
        "fbclid",
        "gclid",
        "li_fat_id",
        "lipi",
        "midSig",
        "miniProfileUrn",
        "origin",
        "rcm",
        "refId",
        "ref",
        "trackingId",
        "trk",
        "utm_campaign",
        "utm_content",
        "utm_medium",
        "utm_source",
        "utm_term",
    }

    def __init__(self):
        self.config = Passwords().get_db_config()

    @contextmanager
    def connect(self):
        connection = pymysql.connect(
            host=self.config["host"],
            user=self.config["user"],
            password=self.config["password"],
            database=self.config["database"],
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        try:
            yield connection
        finally:
            connection.close()

    def normalize_url(self, url, base_url=None):
        if not url:
            return None

        absolute_url = urljoin(base_url or "", url.strip())
        parsed = urlparse(absolute_url)

        scheme = parsed.scheme.lower() or "https"
        netloc = parsed.netloc.lower()
        if netloc.startswith("www."):
            netloc = netloc[4:]

        path = parsed.path.rstrip("/")
        query_items = [
            (key, value)
            for key, value in parse_qsl(parsed.query, keep_blank_values=True)
            if key not in self.TRACKING_PARAMS and not key.startswith("utm_")
        ]
        query = urlencode(sorted(query_items), doseq=True)

        return urlunparse((scheme, netloc, path, "", query, ""))

    def is_duplicate(self, post_url, platform):
        normalized_url = self.normalize_url(post_url)
        if not normalized_url:
            return True

        raw_table = f"{platform}_raw"
        filtered_table = f"{platform}_filtered"
        query = f"""
            SELECT
                EXISTS(SELECT 1 FROM {raw_table} WHERE post_url = %s LIMIT 1)
                OR
                EXISTS(SELECT 1 FROM {filtered_table} WHERE post_url = %s LIMIT 1)
                AS is_duplicate
        """

        with self.connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(query, (normalized_url, normalized_url))
                row = cursor.fetchone()
                return bool(row and row["is_duplicate"])

    def insert_raw(self, platform, keyword, content, post_url):
        normalized_url = self.normalize_url(post_url)
        if not normalized_url:
            return False

        query = f"""
            INSERT INTO {platform}_raw (keyword, content, post_url)
            VALUES (%s, %s, %s)
        """

        try:
            with self.connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (keyword, content, normalized_url))
                connection.commit()
            return True
        except IntegrityError:
            return False
