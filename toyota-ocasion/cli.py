import os
import logging
from glob import glob

import click
from loaders.base import BaseLoader
from mappers.toyota import ToyotaMapper
from scrapers.toyota import ToyotaScraper, ToyotaJson2CSV
from transformers.toyota import ToyotaTransformer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# crate cli group


@click.group()
def cli():
    pass


@cli.command()
@click.option('--limit', '-l', type=int, help='Limit of items to scrape')
@click.option('--page_size', '-ps', type=int, default=100, help='Number of items per request')
@click.option('--debug', type=click.Choice(map(str, [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])), default="20", help='Debug mode')
def scrape(limit, page_size, debug):
    logger.setLevel(int(debug))

    scraper = ToyotaScraper(limit=limit, page_size=page_size)
    output_file = scraper.scrape()
    logger.info(f"Scraped output file: {output_file}")


def get_last_modified_file(folder='data/scraped', brand='', extension='.json'):
    files = glob(f'{folder}{os.sep}{brand}*{extension}')
    if not files:
        logger.error("No files found")
        return

    input_file = max(files, key=os.path.getctime)
    return input_file


@cli.command()
@click.option('--input_file', '-i', type=str, help='Path to input file')
@click.option('--debug', type=click.Choice(map(str, [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])), default="20", help='Debug mode')
def parse(input_file, debug):
    logger.setLevel(int(debug))

    if input_file is None:
        # find last modified file in data/scraped
        input_file = get_last_modified_file(brand='toyota')
        logger.info(f"Using last modified file: {input_file}")

    parser = ToyotaJson2CSV()
    output_file = parser.run(input_file)
    logger.info(f"Parsed output file: {output_file}")


@cli.command()
@click.option('--input_file', '-i', type=str, help='Path to input file')
@click.option('--debug', type=click.Choice(map(str, [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])), default="20", help='Debug mode')
def transform(input_file, debug):
    logger.setLevel(int(debug))

    if input_file is None:
        # find last modified file in data/scraped
        input_file = get_last_modified_file(brand='toyota', extension='.csv')
        logger.info(f"Using last modified file: {input_file}")

    proc = ToyotaTransformer()
    output_file = proc.run(input_file=input_file)
    logger.info(f"Transformed output file: {output_file}")


@cli.command('map')
@click.option('--input_file', '-i', type=str, help='Path to input file')
@click.option('--debug', type=click.Choice(map(str, [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])), default="20", help='Debug mode')
def f_map(input_file, debug):
    logger.setLevel(int(debug))

    if input_file is None:
        # find last modified file in data/scraped
        input_file = get_last_modified_file(
            folder='data/transformed', brand='toyota', extension='.csv')
        logger.info(f"Using last modified file: {input_file}")

    proc = ToyotaMapper()
    print("")

    output_file = proc.run(input_file=input_file)
    logger.info(f"Mapped output file: {output_file}")


@cli.command()
@click.option('--input_file', '-i', type=str, help='Path to input file')
@click.option('--db_file', '-db', type=str, default='streamlits/coches.db', help='Path to sqlite database')
@click.option('--mode', '-m', type=click.Choice(['replace', 'append']), default='append', help='Mode to save data')
@click.option('--debug', type=click.Choice(map(str, [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])), default="20", help='Debug mode')
def load(input_file, db_file, mode, debug):
    logger.setLevel(int(debug))

    if input_file is None:
        # find last modified file in data/scraped
        input_file = get_last_modified_file(
            folder='data/mapped', brand='toyota', extension='.csv')
        logger.info(f"Using last modified file: {input_file}")

    loader = BaseLoader()
    loader.run(input_file, db_file, mode)
    logger.info(f"Data loaded into sqlite database")


@cli.command()
@click.option('--db_file', '-db', type=str, default='streamlits/coches.db', help='Path to sqlite database')
@click.option('--debug', type=click.Choice(map(str, [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])), default="20", help='Debug mode')
def update_last_seen(db_file, debug):
    logger.setLevel(int(debug))

    loader = BaseLoader()
    loader.update_last_seen(db_file)
    logger.info(f"Table 'offers_last_seen_available' has been updated")

    
if __name__ == '__main__':
    cli()
