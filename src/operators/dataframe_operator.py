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

    @staticmethod
    def remove_timezone(df: pd.DataFrame) -> pd.DataFrame:
        for column in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[column]):
                # Convert timezone-aware datetime objects to naive ones (without timezone)
                df[column] = df[column].apply(lambda x: x.replace(tzinfo=None) if pd.notnull(x) else x)
        return df

    # @staticmethod
    # def update_df_from_df(df_to_update, df_update_from, left_on, right_on):
    #     # Merge df_to_update with df_update_from on matching columns
    #     merged_df = df_to_update.merge(df_update_from, left_on=left_on, right_on=right_on, how="left", suffixes=("", "_update"))
    #
    #     # Iterate through columns to update df_to_update from df_update_from
    #     for col in merged_df.columns:
    #         if col.endswith("_update"):
    #             # Determine the original column name by removing '_update' suffix
    #             original_col = col[:-7]  # '_update' is 7 characters long
    #
    #             # Check if the original column exists in df_to_update
    #             if original_col in df_to_update.columns:
    #                 # Update df_to_update with values from the merged DataFrame
    #                 # Prefer values from the '_update' column, falling back to the original where '_update' is NaN
    #                 df_to_update[original_col] = merged_df[col].combine_first(merged_df[original_col])
    #
    #     return df_to_update
    @staticmethod
    def update_df_from_df(df_to_update, df_update_from, left_on, right_on, column_mapper=None):
        # Merge df_to_update with df_update_from on matching columns
        merged_df = df_to_update.merge(df_update_from, left_on=left_on, right_on=right_on, how="left", suffixes=("", "_update"))

        # If column_mapper is provided, use it to update specified columns
        if column_mapper:
            for original_col, update_col in column_mapper.items():
                if original_col == update_col:
                    update_col += "_update"  # Add the '_update' suffix to the update_col
                if original_col in df_to_update.columns and update_col in merged_df.columns:
                    df_to_update[original_col] = merged_df[update_col].combine_first(merged_df[original_col])
        else:
            # Iterate through columns to update df_to_update from df_update_from
            for col in merged_df.columns:
                if col.endswith("_update"):
                    # Determine the original column name by removing '_update' suffix
                    original_col = col[:-7]  # '_update' is 7 characters long
                    # Update df_to_update with values from the merged DataFrame
                    # Prefer values from the '_update' column, falling back to the original where '_update' is NaN
                    df_to_update[original_col] = merged_df[col].combine_first(merged_df[original_col])
        return df_to_update
