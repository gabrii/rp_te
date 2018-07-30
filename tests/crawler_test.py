from mock import Mock
import pytest
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


@pytest.mark.parametrize("text, links", [
    ("Foo bar", []),
    (
            "epository&quot;,&quot;url&quot;:&quot;https://github.com/don/cordova-plugin-hello&quot;},&quot;client_id",
            ["https://github.com/don/cordova-plugin-hello"]
    ),
    (
            LINKS_SOURCE,
            LINKS
    )
])
def test_extract_repo_links(crawler, text, links):
    extracted_links = crawler.extract_links(text)
    assert links == extracted_links


def test_extract_issue_links(crawler):
    extracted_links = crawler.extract_links("""
    <a title="foo" data-hydro-click="{&quot;event_type&quot;:&quot;search_result.click&quot;,&quot;payload&quot;:
    :&quot;MDExOlB1bGxSZXF1ZXN0MjA0MzQ3NjM5&quot;,&quot;model_name&quot;:&quot;Issue
    &quot;,&quot;url&quot;:&quot;https://github.com/nathanleiby/rc2/pull/1&quot;},&quot;
    """)
    assert ["https://github.com/nathanleiby/rc2/pull/1"] == extracted_links


def text_extract_wiki_links(crawler):
    extracted_links = crawler.extract_links("""<a title="Foo" data-hydro-click="{&quot;event_type&quot;:&quot;
    2634440,&quot;global_relay_id&quot;:&quot;MDEwOlJlcG9zaXRvcnkyNjM0NDQw&quot;,&quot;model_name&quot;:&quot;
    Repository&quot;,&quot;url&quot;:&quot;https://github.com//cmaes/hyperprojection/wiki/Foo&quot;},&quot;client_id""")
    assert ["https://github.com//cmaes/hyperprojection/wiki/Foo&"] == extracted_links


def test_search(crawler, mocker):
    mocker.patch("src.crawler.Crawler.get", return_value=LINKS_SOURCE)
    search_links = crawler.search(["Hello", "world!"])
    assert search_links == LINKS


def test_search_bad_type(crawler):
    with pytest.raises(ValueError):
        crawler.search(["Hello"], "bad type")
