# Github Crawler (Technical Evaluation)
Temporal repository for ongoing interview process, it's only public in order to get Travis & Codecov _(The company name and original exercise statement 
is not commited, to preserve the validity of their future evaluations)._


[![Build Status](https://travis-ci.org/gabrii/rp_te.svg?branch=master)](https://travis-ci.org/gabrii/rp_te)
[![codecov](https://codecov.io/gh/gabrii/rp_te/branch/master/graph/badge.svg)](https://codecov.io/gh/gabrii/rp_te)


## Installation

```bash
$ pip install -r requirements.txt
```

## Usage

The crawler can be called directly, passing the parameters as json through stdin, and the results will come out of stdout.

```bash
$ python crawler.py
{
  "keywords": [
    "python",
    "django-rest-framework",
    "jwt"
  ],
  "proxies": [
    "194.126.37.94:8080",
    "13.78.125.167:8080"
  ],
  "type": "Repositories"
}
[
    {
        "url": "https://github.com/GetBlimp/django-rest-framework-jwt",
        "extra": {
            "owner": "GetBlimp",
            "language_stats": {
                "Python": 100.0
            }
        }
    },
    {
        "url": "https://github.com/lock8/django-rest-framework-jwt-refresh-token",
        "extra": {
            "owner": "lock8",
            "language_stats": {
                "Python": 96.6,
                "Makefile": 3.4
            }
        }
    },
    ...
]
$ cat input.json | python crawler.py > output.json 

```

Alternatively, you can use the module directly:
```python
from crawler import Crawler

c = Crawler() # Or Crawler(proxies=["..."])

# c.search(keywords, type)
# Returns results URLs
c.search(["Hello", "world!"], "Issues")

# c.search_extra(keywords, type)
# Returns results URLs, owners, and language stats when performing a repository search.
c.search_extra(["Hello", "world!"], "Repositories") 
```