import ast
import logging

import pandas as pd
from transformers.base import BaseTransformer

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ToyotaTransformer(BaseTransformer):

    name = "toyota"

    def transform(self, df, **kwargs):

        df.drop(columns=["images"], inplace=True)

        # expand dict columns
        dict_cols = [
            "vehicleStatus",
            "warranty",
            "mileage",
            "history",
            "price",
            "insuranceQuote",
            "vehicleValue",
            "ucProgram",
            "product",
            "enrichmentStatus",
            "dealer",
        ]
        dict_cols = [k for k, v in df.head(
            1).to_dict().items() if isinstance(v, dict)]

        for col in dict_cols:
            if col in df.columns:
                try:
                    dft = pd.json_normalize(
                        df[col].fillna("{}").apply(ast.literal_eval)
                    )
                    logger.debug(
                        f"Normalized dict col {col} with ast.literal_eval")
                except Exception as e:
                    dft = df[col].apply(pd.Series)
                    logger.debug(f"Normalized dict col {col} with pd.Series")

                df = df.join(dft.rename(columns=lambda x: f"{col}-{x}")).drop(
                    col, axis="columns"
                )
                logger.debug(f"Expanded dict column: {col}")
        logger.info(f"Current shape of df: {df.shape}")

        # drop list type columns
        list_cols = [k for k, v in df.head(
            1).to_dict().items() if isinstance(v, list)]
        df.drop(list_cols, axis=1, inplace=True)
        logger.debug(f"Dropped list cols: {';'.join(list_cols)}")
        logger.info(f"Current shape of df: {df.shape}")

        # drop columns
        df.drop(
            [
                "enrichmentStatus-financingEnrichmentStatus",
                # 'enrichmentStatus-insuranceEnrichmentStatus'
            ],
            axis=1,
            inplace=True,
            errors="ignore",
        )

        # drop na cols
        cols_to_drop = df.columns[df.count() == 0].tolist()
        df.dropna(axis=1, how="all", inplace=True)
        logger.debug(f"Dropped all null cols: {';'.join(cols_to_drop)}")
        logger.info(f"Current shape of df: {df.shape}")

        # drop numeric columns with just one different value
        cols_to_drop = (
            df.select_dtypes("number")
            .columns[df.select_dtypes("number").nunique() == 1]
            .tolist()
        )
        df.drop(cols_to_drop, axis=1, inplace=True)
        logger.debug(f"Dropped numeric unique cols: {';'.join(cols_to_drop)}")
        logger.info(f"Current shape of df: {df.shape}")

        # drop list type columns
        list_cols = []
        for col in df.columns:
            s = df[col].apply(lambda x: isinstance(x, list)).sum()
            if s > 0:
                list_cols.append(col)
        df.drop(list_cols, axis=1, inplace=True)
        logger.debug(f"Dropped list cols: {';'.join(list_cols)}")
        logger.info(f"Current shape of df: {df.shape}")

        # drop dict columns
        dict_cols = []
        for col in df.columns:
            s = df[col].apply(lambda x: isinstance(x, dict)).sum()
            if s > 0:
                dict_cols.append(col)
        df.drop(dict_cols, axis=1, inplace=True)
        logger.debug(f"Dropped dict cols: {';'.join(dict_cols)}")
        logger.info(f"Current shape of df: {df.shape}")

        # drop dup cols
        cols_to_drop = df.columns[df.T.duplicated()].tolist()
        df.drop(cols_to_drop, axis=1, inplace=True)
        logger.debug(f"Dropped duplicated cols: {';'.join(cols_to_drop)}")
        logger.info(f"Current shape of df: {df.shape}")

        # drop columns with 1 unique value
        cols_to_drop = df.columns[df.nunique() == 1].tolist()
        df.drop(cols_to_drop, axis=1, inplace=True)
        logger.debug(f"Dropped nunique=1 cols: {';'.join(cols_to_drop)}")
        logger.info(f"Current shape of df: {df.shape}")

        # drop cols with all nulls
        cols_to_drop = df.columns[df.count() == 0].tolist()
        df.dropna(axis=1, how="all", inplace=True)
        logger.debug(f"Dropped all null cols: {';'.join(cols_to_drop)}")
        logger.info(f"Current shape of df: {df.shape}")

        # Fix date cols format
        for col in df.filter(like="Date").columns.tolist():
            df[col] = pd.to_datetime(
                df[col], errors="coerce").dt.strftime("%Y-%m-%d")
            logger.debug(f"Transformed date column: {col}")

        df["car_url"] = df["id-0"].apply(
            lambda x: f"https://www.toyota.es/coches-segunda-mano/ficha.toyota-yaris-cross-2024-5p-automatico-hibrido-{x}"
        )

        # add timestamp column
        df["last_seen"] = pd.Timestamp.now()
        df["last_seen_date"] = df["last_seen"].dt.strftime("%Y-%m-%d")

        return df
