import pytest
from mock import Mock

from src import Crawler


@pytest.fixture()
def crawler() -> Crawler:
    return Crawler()


def test_init(crawler):
    pass


def test_construct_url(crawler):
    url = crawler.construct_url(
        ["Hello", "world!"],
        "Repositories"
    )
    assert "https://github.com/search?q=Hello+world%21&type=Repositories" == url


def test_construct_url_utf(crawler):
    url = crawler.construct_url(
        ["Hello", "✓"],
        "Repositories"
    )
    assert "https://github.com/search?q=Hello+%E2%9C%93&type=Repositories" == url


def test_get(crawler, mocker):
    mocker.patch("requests.get", return_value=Mock(text="Foo"))
    source = crawler.get("https://github.com/")
    assert "Foo" in source


LINKS_SOURCE = """Repository&quot;,&quot;url&quot;:&quot;https://github.com/docker/dockercloud-hello-world&quot;}
,&quot;client_id&quot;:&quot;1102215342.1532969344&quot;,&quot;originating_request_id&quot;:&qc49AA&quot;itory&q
uot;,&quot;url&quot;:&quot;https://github.com/knightking100/hello-worlds&quot;},&quot;client_id&quot;:&q"""
LINKS = ["https://github.com/docker/dockercloud-hello-world", "https://github.com/knightking100/hello-worlds"]


@pytest.mark.parametrize("test_description, text, links", [
    (
            'No links',
            "Empty source",
            [],
    ),
    (
            "One repository link",
            "epository&quot;,&quot;url&quot;:&quot;https://github.com/don/cordova-plugin-hello&quot;},&quot;client_id",
            ["https://github.com/don/cordova-plugin-hello"],
    ),
    (
            "Two repository links",
            LINKS_SOURCE,
            LINKS,
    ),
    (
            "One issue link",
            """<a title="foo" data-hydro-click="{&quot;eventt;search_result.click&quot;,&quot;payload&quot;:
        :&quot;MDExOlB1bGxSZXF1ZXN0MjA0MzQ3NjM5&quot;,&quot;model_name&quot;:&quot;Issue
        &quot;,&quot;url&quot;:&quot;https://github.com/nathanleiby/rc2/pull/1&quot;},&quot;""",
            ["https://github.com/nathanleiby/rc2/pull/1"],
    ),
    (
            "One wiki link",
            """<a title="Foo" data-hydro-click="{&quot;event_type&quot;:&quot;
        2634440,&quot;global_relay_id&quot;:&quot;MDEwOlJlcG9zaXRvcnkyNjM0NDQw&quot;,&quot;model_name&quot;:&quot;
        Repository&quot;,&quot;url&quot;:&quot;https://github.com//cmaes/hypection/wiki/Foo&quot;},&quot;client_id""",
            ["https://github.com//cmaes/hypection/wiki/Foo"],
    )
])
def test_extract_links(crawler, test_description, text, links):
    """Tries to extract links from repo, issue, and wiki search results."""
    extracted_links = crawler.extract_links(text)
    assert links == extracted_links, test_description


def test_search(crawler, mocker):
    mocker.patch("src.crawler.Crawler.get", return_value=LINKS_SOURCE)
    results = crawler.search(["Hello", "world!"])
    assert results == [{"url": url} for url in LINKS]


def test_search_extra(crawler, mocker):
    mocker.patch("src.crawler.Crawler.get", return_value=LINKS_SOURCE)
    results = crawler.search_extra(["Hello", "world!"])
    assert results == [
        {"url": "https://github.com/docker/dockercloud-hello-world", "owner": "docker"},
        {"url": "https://github.com/knightking100/hello-worlds", "owner": "knightking100"}
    ]


def test_search_bad_type(crawler):
    with pytest.raises(ValueError):
        crawler.search(["Hello"], "bad type")


def test_extract_language_info(crawler):
    source = """ <span class="language-color" aria-label="Python 95.9%" style="width:95.9%; background-color:#3572A5;" 
        itemprop="keywords">Python</span><span class="language-color" aria-label="Tcl 4.1%" style="width:4.1%;
        background-color:#e4cc98;" itemprop="keywords">Tcl</span>"""
    language_info = crawler.extract_language_info(source)
    assert {"Python": 95.9, "Tcl": 4.1} == language_info
