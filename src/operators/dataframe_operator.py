import os

import pandas as pd


class DataFrameOperator:
    @staticmethod
    def merge_csv(directory):
        """Merge all CSV files in the specified directory into a single DataFrame."""
        csv_files = [f for f in os.listdir(directory) if f.endswith(".csv")]
        if not csv_files:
            raise FileNotFoundError("No CSV files found in the directory.")

        dataframes = []
        for f in csv_files:
            try:
                df = pd.read_csv(os.path.join(directory, f))
                dataframes.append(df)
            except pd.errors.EmptyDataError:
                print(f"Warning: '{f}' is empty and will be skipped.")
            except pd.errors.ParserError as e:
                print(f"Error reading '{f}': {e}. File will be skipped.")

        if not dataframes:
            return pd.DataFrame()

        return pd.concat(dataframes, ignore_index=True)
