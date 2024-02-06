import pandas as pd
from loguru import logger

REQUIRED_COLUMNS = [
    "timestamp",
    "timestamp_local",
    "ax",
    "ay",
    "az",
    "fall_state",
]


class DataValidator:
    def __init__(
        self,
        data: pd.DataFrame,
        filename: str,
        required_columns: list = REQUIRED_COLUMNS,
    ):
        self.data = data
        self.required_columns = required_columns
        self.filename = filename

    def validate(self):
        self.check_all_columns()
        self.check_null_values()
        self.check_duplicated_rows()
        self.drop_timestamp()
        self.rename_timestamp_local()
        return self.data

    def check_all_columns(self):
        logger.info(f"Checking all columns in {self.filename}")
        missing_columns = set(self.required_columns) - set(self.data.columns)
        if missing_columns:
            logger.error(f"Missing columns: {missing_columns}")
            raise ValueError(f"Missing columns: {missing_columns}")
        logger.info("All columns present")

    def check_null_values(self):
        logger.info(f"Checking for null values in {self.filename}")
        if self.data.isnull().values.any():
            logger.error("Null values found")
            raise ValueError("Null values found")
        logger.info("No null values found")

    def check_duplicated_rows(self):
        logger.info(f"Checking for duplicated rows in {self.filename}")
        if self.data.duplicated().any():
            logger.error("Duplicated rows found")
            raise ValueError("Duplicated rows found")
        logger.info("No duplicated rows found")

    def drop_timestamp(self):
        if "timestamp" in self.data.columns:
            logger.info(f"Dropping 'timestamp' column in {self.filename}")
            self.data.drop(columns=["timestamp"], inplace=True)
            logger.info("'timestamp' column dropped")
        else:
            logger.warning("'timestamp' column not found; cannot drop")

    def rename_timestamp_local(self):
        if "timestamp_local" in self.data.columns:
            logger.info(f"Renaming 'timestamp_local' to 'timestamp' in {self.filename}")
            self.data.rename(columns={"timestamp_local": "timestamp"}, inplace=True)
            logger.info("'timestamp_local' column renamed to 'timestamp'")
        else:
            logger.warning("'timestamp_local' column not found; cannot rename")
