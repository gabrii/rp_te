import json
import random
import re
from typing import List, Dict
from urllib.parse import quote_plus

import requests

quote = "&quot;"

links_exp = '"url":"(.*?)(?=")'.replace('"', quote)  # Extract links from HTML "data-..." param
languages_exp = 'color\" aria-label=\"(.*?)(?=\%)'  # Extract Language info from aria param. Format: "Lang X.Y"(%)


class Crawler:

    def __init__(self, proxies: List[str] = None):
        """Crawler constructor. If proxies are given, randomly chooses one for all its lifetime."""
        if proxies:
            self.proxy = random.choice(proxies)
        else:
            self.proxy = None

        # Compile regex once on initialization
        self.links_compiled_exp = re.compile(links_exp)
        self.languages_compiled_exp = re.compile(languages_exp)

    def search(self, keywords: List[str], _type: str = "") -> List[Dict]:
        """Returns a list with a dictionary containing the "url" for each repository."""
        url = self.construct_url(keywords, _type)
        source = self.get(url)
        links = self.extract_links(source)
        return [{"url": url} for url in links]

    def search_extra(self, keywords: List[str], _type: str = "") -> List[Dict]:
        """Returns a list with a dictionary containing the "url", "owner", and "language_stats" for each repository."""
        results = self.search(keywords, _type)

        if _type not in {'', 'Repositories'}:
            # If it's not a repository, return what we have so far.
            return results

        # Extend with owner (from URL) and language stats (extra request)
        return [
            {
                **r,
                "extra": {
                    "owner": r['url'].split('/')[-2],
                    "language_stats": self.extract_language_info(
                        self.get(r['url'])
                    )
                }
            } for r in results
        ]

    @staticmethod
    def construct_url(keywords: List[str], _type: str) -> str:
        """Returns the search URL."""
        if _type not in {"", "Repositories", "Issues", "Wikis"}:
            raise ValueError("Unrecognized search type")
        return "https://github.com/search?q={0}&type={1}".format(quote_plus(' '.join(keywords)),
                                                                 quote_plus(_type))

    def get(self, url: str) -> str:
        response = requests.get(url, proxies={"http": self.proxy})
        return response.text

    def extract_links(self, source: str) -> List[str]:
        """Extracts repo/issue/wiki links from the search html source code."""
        return self.links_compiled_exp.findall(source)

    def extract_language_info(self, source: str) -> Dict[str, float]:
        """Extracts a repository's languages and usage percent from the repo's landing page html source code."""
        languages = self.languages_compiled_exp.findall(source)
        language_info = {}
        for lang in languages:
            name = ' '.join(lang.split()[:-1])
            percent = float(lang.split()[-1])  # %
            language_info[name] = percent
        return language_info

    @classmethod
    def oneshot(cls, keywords: List[str], _type: str = "", proxies: List[str] = None) -> List[Dict]:
        """Used for one-shot searches (initializes the crawler for a single use and returns the result).
            Used by main."""
        c = cls(proxies)
        return c.search_extra(keywords, _type)

    @classmethod
    def main(cls):
        """Gets the parameters from standard input as json, and standard outputs extra search results as json."""
        lines = [input()]
        while '}' not in lines[-1]:
            lines.append(input())
        s = '\n'.join(lines).replace('"type"', '"_type"')  # Replace type to prevent collision with built in keyword
        print(json.dumps(
            cls.oneshot(**json.loads(s)),
            indent=4
        ))


if __name__ == "__main__":
    Crawler.main()
