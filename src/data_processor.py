import os
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger

from motion_features import MotionFeatureCalculator


class DataProcessor:
    def __init__(self, raw, processed):
        self.raw = Path(raw)
        self.processed = Path(processed)

    def load_data(self, filename):
        logger.info(f"Loading data from {filename}")
        file_path = self.raw / filename
        if file_path.exists():
            logger.info(f"File found at {file_path}")
            return pd.read_csv(file_path)
        else:
            logger.error(f"No file found at {file_path}")
            raise FileNotFoundError(f"No file found at {file_path}")

    def process_data(self, data):
        try:
            motion_feature_calculator = MotionFeatureCalculator(
                data, "timestamp", ["ax", "ay", "az"]
            )
            logger.info("Processing data")
            processed_data = motion_feature_calculator.calculate_all_features()
            logger.info("Data processed")
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            raise e
        return processed_data

    def is_already_processed(self, file):
        processed_file_name = f"processed_{file}"
        processed_file_path = self.processed / processed_file_name
        return processed_file_path.exists()

    def process_file(self, file):
        if self.is_already_processed(file):
            logger.info(f"File {file} already processed. Skipping...")
            return

        try:
            data = self.load_data(file)
            processed_data = self.process_data(data)
            self.save_data(processed_data, f"processed_{file}")
            logger.info(f"File {file} processed successfully")
        except FileNotFoundError as e:
            logger.error(f"File not found: {e}")
        except Exception as e:
            logger.error(f"Error processing file: {e}")

    def save_data(self, data, filename):
        try:
            logger.info(f"Saving data to {filename}")
            save_path = self.processed / filename
            data.to_csv(save_path, index=False)
            logger.info(f"Data saved to {save_path}")
        except Exception as e:
            logger.error(f"Error saving file: {e}")
            raise e


def setup_directories():
    assert os.path.exists("data"), logger.error("Data directory does not exist")
    assert os.path.exists("data/processed"), logger.error(
        "Processed data directory does not exist"
    )
    assert os.path.exists("data/raw"), logger.error("Raw data directory does not exist")

    PATH_TO_PROCESSED = "data/processed"
    PATH_TO_RAW = "data/raw"

    if not os.path.exists(PATH_TO_PROCESSED):
        logger.info(f"Creating processed data directory at {PATH_TO_PROCESSED}")
        os.makedirs(PATH_TO_PROCESSED)

    return PATH_TO_RAW, PATH_TO_PROCESSED


def main():
    logger.info("Starting data processing")

    PATH_TO_RAW, PATH_TO_PROCESSED = setup_directories()
    data_processor = DataProcessor(PATH_TO_RAW, PATH_TO_PROCESSED)

    logger.info("Processing files")
    for file in os.listdir(PATH_TO_RAW):
        data_processor.process_file(file)


if __name__ == "__main__":
    main()
