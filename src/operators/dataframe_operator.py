import logging
import os

import pandas as pd

logger = logging.getLogger(__name__)


class DataFrameOperator:
    @staticmethod
    def merge_csv(directory: str) -> pd.DataFrame:
        """Merge all CSV files in the specified directory into a single DataFrame."""
        csv_files = [f for f in os.listdir(directory) if f.endswith(".csv")]
        if not csv_files:
            logger.warning("No CSV files found in the directory.")
            raise FileNotFoundError("No CSV files found in the directory.")

        dataframes = []
        for f in csv_files:
            try:
                df = pd.read_csv(os.path.join(directory, f))
                dataframes.append(df)
                logger.info(f"Successfully read CSV file {f}")
            except pd.errors.EmptyDataError:
                logger.warning(f"Warning: '{f}' is empty and will be skipped.")
            except pd.errors.ParserError as e:
                logger.error(f"Error reading '{f}': {e}. File will be skipped.")

        if not dataframes:
            logger.info("No dataframes were created. Returning an empty dataframe.")
            return pd.DataFrame()

        merged_df = pd.concat(dataframes, ignore_index=True)
        logger.info("Successfully merged all CSV files.")
        return merged_df
