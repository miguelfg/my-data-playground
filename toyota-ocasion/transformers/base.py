import os
import pandas as pd
from datetime import datetime

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BaseTransformer:

    def __init__(self, limit=None):
        self.limit = limit
        self.name = 'base_transformer'
        self.ofolder = 'data/transformed/'

    def generate_output_filename(self, input_file):
        input_name = input_file.split(os.sep)[-1] if os.sep in input_file else input_file
        output_file = f"{self.ofolder}{os.sep}{input_name}"
        return output_file
    
    def read(self, input_file, **kwargs):
        return pd.read_csv(input_file)
    
    def save(self, df: pd.DataFrame, output_file):
        df.to_csv(output_file, index=False)
        logger.info(f"File saved to: {output_file}")

    def transform(self, df, **kwargs):
        raise NotImplementedError
    
    def run(self, input_file, **kwargs):
        df = self.read(input_file, **kwargs)
        df = self.transform(df, **kwargs)
        output_filename = self.generate_output_filename(input_file)
        self.save(df, output_filename)
        return output_filename