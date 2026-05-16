from urllib.parse import quote_plus


class Search:
    """
    Generates search URLs for the social platforms.

    Keywords are optional while this project is under development. If no custom
    list is provided, the LinkedIn test uses a small default list.
    """

    DEFAULT_KEYWORDS = [
        "مطلوب خبير تسويق",
        "مطلوب مسوق رقمي",
        "مطلوب مدير إعلاني",
        "مطلوب وكالة تسويقية",
        "مطلوب فريلانسر تسويق رقمي",
        "نبحث عن خبير تسويق",
        "نبحث عن مسوق رقمي",
        "نبحث عن مدير إعلاني",
        "نبحث عن وكالة تسويقية",
        "نبحث عن فريلانسر تسويق رقمي",
        "نبحث عن فريق فريلانسرز",
        "نبحث عن وكالة تسويقية في الخليج",
        "مطلوب وكالة تسويقية في الخليج",
        "مطلوب وكالة تسويقية في السعودية",
        "مطلوب وكالة تسويقية في الكويت",
        "نبحث عن فريق تسويق رقمي في السعودية",
        "نبحث عن فريق تسويق رقمي في الكويت",
        "نبحث عن فريلانسر تسويق رقمي في السعودية",
        "مطلوب فريلانسر تسويق رقمي في الكويت",
    ]

    def __init__(self, keywords=None):
        self.keywords = [self.clean_keyword(keyword) for keyword in (keywords or self.DEFAULT_KEYWORDS)]

    def clean_keyword(self, keyword):
        return " ".join(str(keyword).strip().split())

    def encode_query(self, keyword):
        return quote_plus(self.clean_keyword(keyword))

    def generate_platform_urls(self, platform):
        platform = platform.lower()
        generators = {
            "twitter": self.generate_twitter_urls,
            "x": self.generate_twitter_urls,
            "instagram": self.generate_instagram_urls,
            "insta": self.generate_instagram_urls,
            "linkedin": self.generate_linkedin_urls,
            "linked": self.generate_linkedin_urls,
        }

        if platform not in generators:
            raise ValueError(f"Unsupported platform: {platform}")

        return generators[platform]()

    def generate_twitter_urls(self):
        urls = []
        for keyword in self.keywords:
            encoded_keyword = self.encode_query(keyword)
            urls.append(f"https://x.com/search?q={encoded_keyword}&src=typed_query&f=live")
        return urls

    def generate_instagram_urls(self):
        urls = []
        for keyword in self.keywords:
            tag = self.clean_keyword(keyword).replace(" ", "_").lstrip("#")
            urls.append(f"https://www.instagram.com/explore/tags/{quote_plus(tag)}/")
        return urls

    def generate_linkedin_urls(self):
        urls = []
        for keyword in self.keywords:
            encoded_keyword = self.encode_query(keyword)
            urls.append(
                "https://www.linkedin.com/search/results/content/"
                f"?keywords={encoded_keyword}"
                '&datePosted=%5B%22past-week%22%5D'
                '&sortBy=%22date_posted%22'
            )
        return urls


if __name__ == "__main__":
    search_engine = Search()
    links = search_engine.generate_linkedin_urls()
    print(f"Generated {len(links)} LinkedIn search links.")
    print(f"First link: {links[0]}")
