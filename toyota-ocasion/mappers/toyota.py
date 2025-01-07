from mappers.base import BaseMapper

import logging
import pandas as pd
from yaml import safe_load

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ToyotaMapper(BaseMapper):
    name = 'toyota_mappings'

    def transform(self, df, mappings):
        df = super().transform(df, mappings)

        # drop all columns not in renamings values
        renamed_cols = []
        for item in self.get_or_empty(mappings, 'columns:renamings'):
            old_value, new_value = [e.strip() for e in item.split(' -> ')]
            renamed_cols.append(new_value)

        cols_to_drop = [col for col in df.columns if col not in renamed_cols]
        cols_to_drop.remove('source')
        cols_to_drop.remove('source_url')
        df.drop(columns=cols_to_drop, inplace=True, errors='ignore')
        logger.debug(f"Dropped unwanted columns: {';'.join(cols_to_drop)}")
        
        logger.info(f"Current shape of df: {df.shape}")

        return df

    