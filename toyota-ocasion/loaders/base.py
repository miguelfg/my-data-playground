import logging
import sqlite3

import pandas as pd

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class BaseLoader:
    name = 'base_loader'

    def __init__(self):
        self.table_name = 'offers_history'

    def read_data(self, input_file):
        return pd.read_csv(input_file)

    def get_table_columns(self, db_file):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        # read columns list in schema of table 'coches'
        cursor.execute(f"PRAGMA table_info({self.table_name})")
        result = [description[1] for description in cursor]
        cursor.close()
        logger.debug(f"Columns in table {self.table_name}:\n {';'.join(result)}")
        return result

    def save(self, df: pd.DataFrame, db_file, mode='replace'):
        schema_cols = self.get_table_columns(db_file)
        logger.debug(f"Columns in schema: {';'.join(schema_cols)}")

        cols_in_schema = [col for col in df.columns if col in schema_cols]
        cols_not_in_schema = [
            col for col in df.columns if col not in schema_cols]
        prev_shape = df.shape
        df = df[cols_in_schema]
        post_shape = df.shape
        logger.debug(
            f"Columns were not in schema: {';'.join(cols_not_in_schema)}")
        logger.info(
            f"Reduced df to columns in coches schema, from shape {prev_shape} to {post_shape}")

        df.to_sql(self.table_name,
                  sqlite3.connect(db_file),
                  if_exists=mode,
                  index=False,
                  )

        logger.info(f"Data saved to sqlite: {db_file}")

    def run(self, input_file, db_file, mode):
        df = self.read_data(input_file)
        self.save(df, db_file, mode)
        return db_file

    def read_last_history(self, db_file):
        query = f"SELECT *, max(last_seen) AS remove_col FROM {self.table_name} WHERE car_sale_status = 'Disponible' GROUP BY car_vin;"
        df = pd.read_sql(query, sqlite3.connect(db_file))
        df.drop(columns=['remove_col'], inplace=True)
        return df
    
    def flush_table(self, db_file, table=None):
        if not table:
            table = self.table_name

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table};")
        conn.commit()
        cursor.close()
        logger.info(f"Table {table} has been flushed")

    def update_last_seen(self, db_file):
        df = self.read_last_history(db_file)
        logger.info(f"Rows read from history offers: {df.shape[0]}")
        
        if df.shape[0] > 0:
            self.flush_table(db_file, table='offers_last_seen_available')

            df.to_sql('offers_last_seen_available',
                    sqlite3.connect(db_file),
                    if_exists='replace',
                    index=False,
                    )
            logger.info(f"Data saved to sqlite {db_file} - table 'offers_last_seen_available'")