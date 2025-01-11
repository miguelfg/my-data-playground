import json
import time
import logging
from datetime import datetime

import pandas as pd
import requests as rq

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class BaseScraper:
    get_or_post = 'get'

    def __init__(self, limit=None, page_size=20):
        self.url = ''
        self.limit = limit
        self.name = 'base_scraper'
        self.page_size = page_size
        self.responses = []
        self.ofolder = 'data/scraped/'
        self.headers = {}
        self.params = {}
        self.cookies = {}
        self.json = {}
        self.data = {}
        self.sleep_per_request = 0.5

    def get_url(self, **kwargs):
        url = self.url
        url = url.format(**kwargs)
        logger.debug(f"New url is: {url}")
        return url

    def get_headers(self, **kwargs):
        h = self.headers.copy()
        h.update(kwargs)
        logger.debug(f"New headers are: {h}")
        return h

    def get_json(self, **kwargs):
        j = self.json.copy()
        j.update(kwargs)
        logger.debug(f"New json is: {j}")
        return j

    def get_params(self, **kwargs):
        if 'from_' in kwargs:
            kwargs['from'] = kwargs.pop('from_')
        params = self.params.copy()
        params.update(kwargs)
        logger.debug(f"New params are: {params}")
        return params

    def get_data(self, **kwargs):
        data = self.data.copy()
        data.update(kwargs)
        logger.debug(f"New data is: {data}")
        return data

    def get_total_items(self):
        total_items = self.responses[0]['total']
        logger.info(f"Total items: {total_items} to scrape")
        return total_items

    def get_page(self, url, headers=None, params=None, json=None, data=None):
        logger.debug(f"Getting page url: {url}")
        if self.get_or_post == 'get':
            response = rq.get(url,
                              headers=headers,
                              params=params,
                              cookies=self.cookies,
                              json=json,
                              timeout=10)
        else:
            response = rq.post(url,
                               headers=headers,
                               params=params,
                               cookies=self.cookies,
                               json=json,
                               data=data,
                               timeout=10)

        if str(response.status_code).startswith('2'):
            self.responses.append(response.json())
            return

        logger.error(
            f"Error: Could not scrape the URL - response code {response.status_code}: {response.text}")
        raise ValueError(
            f"Error: Could not scrape the URL - response code {response.status_code}")

    def save_responses(self):
        output_file = f"{self.ofolder}{self.name}-{datetime.now().strftime('%Y%m%d%H%M%S')}.json"

        with open(output_file, 'w') as f:
            json.dump(self.responses, f)
        logger.info(f"Responses saved to {output_file}")

        return output_file

    def scrape_first(self):
        url = self.get_url(page=1, page_size=self.page_size)
        headers = self.get_headers()
        params = self.get_params(page=1, page_size=self.page_size)
        j = self.get_json()
        data = self.get_data()
        self.get_page(url=url, headers=headers,
                      params=params, json=j, data=data)
        logger.info(f"First page added to responses")

    def scrape_rest(self, total_items):
        requests = list(range(2, total_items // self.page_size))
        for r in requests:
            time.sleep(self.sleep_per_request)
            if self.limit and r >= self.limit:
                break

            url = self.get_url()
            headers = self.get_headers()
            params = self.get_params(page=r, page_size=self.page_size)
            j = self.get_json()
            data = self.get_data()
            self.get_page(url=url, headers=headers,
                          params=params, json=j, data=data)
            logger.debug(f"Page {r} added to responses")

            time.sleep(0.5)

    def scrape(self):
        # scrape first page
        self.scrape_first()

        total_items = self.get_total_items()
        logger.info(f"Total items: {total_items}")

        self.scrape_rest(total_items)

        # save responses
        return self.save_responses()


class ParserJson2CSV:

    def __init__(self):
        pass

    def read_data(self, json_file):
        with open(json_file) as f:
            data = json.load(f)
        return data

    def save_data(self, df, json_file):
        # save to csv with datetime timestamp
        output_csv = json_file.replace('.json', '.csv')
        df.to_csv(output_csv, index=False)
        logger.info(f"Parsed data saved to {output_csv}")

        return output_csv

    def parse(self, data):
        dfs = []

        for response in data:
            dft = pd.DataFrame(response['results'])
            dfs.append(dft)

        df = pd.concat(dfs)
        return df

    def run(self, json_file):

        data = self.read_data(json_file)
        df = self.parse(data)
        output_csv = self.save_data(df, json_file)

        return output_csv
