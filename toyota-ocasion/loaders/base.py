import sqlite3
import pandas as pd
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class BaseLoader:
    name = 'base_loader'

    def read_data(self, input_file, **kwargs):
        return pd.read_csv(input_file)

    def get_table_columns(self, db_file):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        # execute a query that reads the columns list in schema of table 'coches'
        cursor.execute("PRAGMA table_info(coches)")
        result = [description[1] for description in cursor]
        return result

    def save(self, df: pd.DataFrame, db_file, mode='replace'):
        schema_cols = self.get_table_columns(db_file)
        logger.debug(f"Columns in schema: {';'.join(schema_cols)}")
        
        cols_in_schema = [col for col in df.columns if col in schema_cols]
        cols_not_in_schema = [col for col in df.columns if col not in schema_cols]
        prev_shape = df.shape
        df = df[cols_in_schema]
        post_shape = df.shape
        logger.debug(f"Columns were not in schema: {';'.join(cols_not_in_schema)}")
        logger.info(f"Reduced df to columns in coches schema, from shape {prev_shape} to {post_shape}")

        df.to_sql('coches', 
                  sqlite3.connect(db_file), 
                  if_exists=mode, 
                  index=False,
        )

        logger.info(f"Data saved to sqlite: {db_file}")

    def run(self, input_file, db_file, mode):
        df = self.read_data(input_file)
        self.save(df, db_file, mode)
        return db_file
