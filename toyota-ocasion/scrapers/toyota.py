import time
import logging

from scrapers.base import BaseScraper, ParserJson2CSV

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ToyotaScraper(BaseScraper):
    """
    Scraper for Toyota used cars
    """
    get_or_post = 'post'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.url = 'https://usc-webcomponents.toyota-europe.com/v1/api/usedcars/results/es/es'
        self.name = 'toyota'
        self.headers = {
            'accept': '*/*',
            'accept-language': 'es-ES,es;q=0.9,en-US;q=0.8,en;q=0.7,de;q=0.6',
            'content-type': 'application/json',
            'origin': 'https://www.toyota.es',
            'priority': 'u=1, i',
            'referer': 'https://www.toyota.es/no-referrer',
            'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'sec-gpc': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        }

        self.json = {
            'uscEnv': 'production',
            'filters': [],
            'filterContext': 'used',
            'offset': 0,
            'resultCount': 20,
            'sortOrder': 'published',
            'distributorCode': '94244',
            'includeActiveFilterAggregations': False,
            'enableBiasedSort': False,
            'usePostFilter': False,
            'enableExperimentalTotalCountQuery': False,
        }

        self.params = {
            'brand': 'toyota',
        }

    def get_total_items(self):
        return self.responses[0]['totalResultCount']

    def scrape_first(self):
        url = self.get_url()
        headers = self.get_headers()
        params = self.get_params()
        j = self.get_json(offset=0, resultCount=self.page_size)
        self.get_page(url=url, headers=headers, params=params, json=j)
        logger.info(f"First page added to responses")

    def scrape_rest(self, total_items):
        # requests = list(range(2, total_items//self.page_size + 2))
        requests = list(range(self.page_size, total_items, self.page_size))
        logger.debug(f"Requests pending to run: {requests}")

        for r in requests:
            if self.limit and r >= self.limit:
                break

            url = self.get_url()
            headers = self.get_headers()
            params = self.get_params()
            j = self.get_json(offset=r, resultCount=self.page_size)
            self.get_page(url=url, headers=headers, params=params, json=j)
            logger.debug(f"Page {r} added to responses")
            time.sleep(0.5)


class ToyotaJson2CSV(ParserJson2CSV):
    pass
