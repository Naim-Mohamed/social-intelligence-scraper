from urllib.parse import quote_plus


class Search:
    """
    Generates search URLs for the social platforms.

    Keywords are optional while this project is under development. If no custom
    list is provided, the LinkedIn test uses a small default list.
    """

    DEFAULT_KEYWORDS = [
        "Hiring Marketing Manager",
        "Campaign Manager",
        "Social Media Manager Saudi",
        "#hiring #UAE #Marketing",
        "Sales Executive Dubai",
        "Brand Builder",
    ]

    def __init__(self, keywords=None):
        self.keywords = keywords or self.DEFAULT_KEYWORDS

    def generate_twitter_urls(self):
        urls = []
        for keyword in self.keywords:
            encoded_keyword = quote_plus(keyword)
            urls.append(f"https://x.com/search?q={encoded_keyword}&src=typed_query&f=live")
        return urls

    def generate_instagram_urls(self):
        urls = []
        for keyword in self.keywords:
            tag = keyword.replace(" ", "")
            urls.append(f"https://www.instagram.com/explore/tags/{quote_plus(tag)}/")
        return urls

    def generate_linkedin_urls(self):
        urls = []
        for keyword in self.keywords:
            encoded_keyword = quote_plus(keyword)
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
