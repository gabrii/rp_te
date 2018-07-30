from typing import List
import re
import requests

from urllib.parse import quote_plus

quote = "&quot;"

links_exp = '"url":"(.*?)(?=")'.replace('"', quote)  # Extract links from HTML "data-..." param
languages_exp = 'color\" aria-label=\"(.*?)(?=\%)'  # Extract Language info from aria param. Format: "Lang X.Y"(%)


class Crawler:

    def __init__(self, proxies: List[str] = None):
        self.proxies = proxies
        self.links_compiled_exp = re.compile(links_exp)

    def search(self, keywords: List[str], _type: str = "") -> List[str]:
        if _type not in {"", "Repositories", "Issues", "Wikis"}:
            raise ValueError("Unrecognized search type")
        url = self.construct_url(keywords, _type)
        source = self.get(url)
        return self.extract_links(source)

    def extra_search(self, keywords: List[str], _type: str = "") -> List[str]:
        pass

    def construct_url(self, keywords: List[str], _type: str) -> str:
        return "https://github.com/search?q={0}&type={1}".format(quote_plus(' '.join(keywords)),
                                                                 quote_plus(_type))

    def get(self, url: str) -> str:
        response = requests.get(url)
        return response.text

    def extract_links(self, source: str) -> List[str]:
        return self.links_compiled_exp.findall(source)
