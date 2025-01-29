import os
import logging

import pandas as pd
from yaml import safe_load

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

COLS_ORDER = [
    "car_brand",
    "car_description",
    "car_package",
    "car_model",
    "car_power_cv",
    "car_power_kw",
    "car_fuel",
    "car_pollution_badge",
    "car_transmission",
    "car_length",
    "car_registration_date",
    "car_model_year",
    "car_mileage",
    "car_price",
    "car_martket_price",
    "car_original_price",
    "car_diff_prices",
    "car_body_type",
    "car_type",
    "car_sale_status",
    "car_rental_type",
    "car_remaining_warranty",
    "car_history_previous_usage",
    "dealer_location",
    "dealer_city",
    "dealer_phone",
    "dealer_website",
    "car_exterior_color",
    "car_interior_color",
    "car_interior_style",
    "car_price_excl_vat",
    "car_catalogue_price",
    "car_vin",
    "manufacturer_car_id",
    "car_license_plate",
    "car_local_model_id",
    "car_height",
    "car_width",
    "car_doors_num",
    "car_seats",
    "car_max_speed",
    "car_acceleration",
    "car_gearbox",
    "car_pollution_badge",
    "car_emissions_class",
    "dealer_id",
    "dealer_name",
    "dealer_email",
    "dealer_zip_code",
    "dealer_province",
    "dealer_geo_lat",
    "dealer_geo_lon",
    "source",
    "source_url",
]


class BaseMapper:
    name = 'base_mapper'

    def __init__(self, mappings_path=None):
        self.mappings_path = mappings_path if mappings_path else f'mappers{os.sep}{self.name}.yaml'
        self.ofolder = f'data{os.sep}mapped'
        if not os.path.exists(self.ofolder):
            os.makedirs(self.ofolder, exist_ok=True)

    def generate_output_filename(self, input_file):
        input_name = input_file.rsplit(
            os.sep, 1)[1] if os.sep in input_file else input_file
        output_file = f"{self.ofolder}{os.sep}{input_name}"
        return output_file

    def read_data(self, input_file, **kwargs):
        return pd.read_csv(input_file)

    def read_mappings(self):
        with open(self.mappings_path) as f:
            return safe_load(f)

    def save(self, df: pd.DataFrame, output_file):
        if not os.path.exists(self.ofolder):
            os.makedirs(self.ofolder)

        df.to_csv(output_file, index=False)
        logger.info(f"File saved to: {output_file}")

    @staticmethod
    def get_or_empty(mappings, keys):
        m2 = mappings.copy()
        try:
            for key in keys.split(':'):
                m2 = m2[key]
        except KeyError:
            return []
        return m2

    def transform(self, df, mappings):
        # keep /drop cols
        cols_to_keep = self.get_or_empty(mappings, 'columns:keep')
        cols_to_keep = [col.strip() for col in cols_to_keep if col.strip(
        ) in df.columns and not col.startswith('#')]
        df = df[cols_to_keep]
        logger.info(f"Dropped unwanted columns")
        logger.info(f"Current shape of df: {df.shape}")

        # run renamings
        renamings_dict = {}
        for item in self.get_or_empty(mappings, 'columns:renamings'):
            old_value, new_value = (e.strip() for e in item.split(' -> '))
            renamings_dict[old_value] = new_value
        logger.info(f"Renamings dict: {renamings_dict}")
        df.rename(columns=renamings_dict, inplace=True)
        logger.info(f"Current shape of df: {df.shape}")

        # run replacements of values
        for col in self.get_or_empty(mappings, 'columns:value_replacements'):
            col_name = list(col.keys())[0]
            values = list(col.values())[0]
            for value in values:
                old_value, new_value = (e.strip() for e in value.split(' -> '))
                df[col_name] = df[col_name].replace(old_value, new_value)

            logger.debug(f"Replaced values in column: {col}")

        # set dtypes
        for col in self.get_or_empty(mappings, 'columns:dtypes:to_int'):
            df[col] = df[col].astype(int)
        for col in self.get_or_empty(mappings, 'columns:dtypes:to_float'):
            df[col] = df[col].astype(float)
        for col in self.get_or_empty(mappings, 'columns:dtypes:to_date'):
            df[col] = pd.to_datetime(
                df[col], errors='coerce').dt.strftime('%Y-%m-%d')
        for col in self.get_or_empty(mappings, 'columns:dtypes:to_datetime'):
            df[col] = pd.to_datetime(df[col], errors='coerce').dt.strftime(
                '%Y-%m-%d - %H:%M:%S')

        logger.info(f"Set dtype for columns")

        # add new static cols
        for item in self.get_or_empty(mappings, 'columns:add'):
            for col, value in item.items():
                df[col] = value
                logger.debug(f"Added column: {col}")

        # extractions from cols
        for item in self.get_or_empty(mappings, 'columns:extract'):
            col, pattern, new_col = (e.strip() for e in item.split(';'))
            pattern = pattern.strip("'")
            df[new_col] = df[col].str.extract(pattern, expand=False)
            logger.debug(
                f"Extracted column: {new_col} with pattern: '{pattern}' from column: {col}")

        logger.debug(f"Current df cols: {';'.join(df.columns.tolist())}")
        # extractions from cols
        cols_order = self.get_or_empty(mappings, 'columns:order')
        if cols_order and len(cols_order) > 1:
            cols_order = [col for col in cols_order if col in df.columns]
        else:
            cols_order = [col for col in COLS_ORDER if col in df.columns]

        cols_order = cols_order + \
            [col for col in df.columns if col not in cols_order]
        df = df[cols_order]
        logger.debug(f"Ordered columns as: {';'.join(cols_order)}")

        return df

    def run(self, input_file, **kwargs):
        df = self.read_data(input_file, **kwargs)
        mappings = self.read_mappings()
        df = self.transform(df, mappings)
        output_filename = self.generate_output_filename(input_file)
        self.save(df, output_filename)
        return output_filename
