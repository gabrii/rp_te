import re
from typing import List, Dict
from urllib.parse import quote_plus

import requests

quote = "&quot;"

links_exp = '"url":"(.*?)(?=")'.replace('"', quote)  # Extract links from HTML "data-..." param
languages_exp = 'color\" aria-label=\"(.*?)(?=\%)'  # Extract Language info from aria param. Format: "Lang X.Y"(%)


class Crawler:

    def __init__(self, proxies: List[str] = None):
        self.proxies = proxies

        # Compile regex once on initialization
        self.links_compiled_exp = re.compile(links_exp)
        self.languages_compiled_exp = re.compile(languages_exp)

    def search(self, keywords: List[str], _type: str = "") -> List[Dict]:
        url = self.construct_url(keywords, _type)
        source = self.get(url)
        links = self.extract_links(source)
        return [{"url": url} for url in links]

    def search_extra(self, keywords: List[str], _type: str = "") -> List[Dict]:
        results = self.search(keywords, _type)
        return [
            {
                **r,
                "owner": r['url'].split('/')[-2]
            } for r in results
        ]

    @staticmethod
    def construct_url(keywords: List[str], _type: str) -> str:
        """Returns the search URL. """
        if _type not in {"", "Repositories", "Issues", "Wikis"}:
            raise ValueError("Unrecognized search type")
        return "https://github.com/search?q={0}&type={1}".format(quote_plus(' '.join(keywords)),
                                                                 quote_plus(_type))

    def get(self, url: str) -> str:
        response = requests.get(url)
        return response.text

    def extract_links(self, source: str) -> List[str]:
        return self.links_compiled_exp.findall(source)

    def extract_language_info(self, source: str) -> Dict[str, float]:
        languages = self.languages_compiled_exp.findall(source)
        language_info = {}
        for lang in languages:
            name = ' '.join(lang.split()[:-1])
            portion = float(lang.split()[-1])
            language_info[name] = portion
        return language_info
