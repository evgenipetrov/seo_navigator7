import datetime
import logging

import pandas as pd
import requests.exceptions

# noinspection PyPackageRequirements
from googleapiclient.discovery import build
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from operators.google_auth_operator import GoogleAuthOperator

logger = logging.getLogger(__name__)


class GSCFetchError(Exception):
    pass


class GoogleSearchConsoleOperator:
    ROW_LIMIT = 25000

    def __init__(self):
        self._service = None

    def set_credentials(self, auth_email):
        auth_service = GoogleAuthOperator(auth_email)
        creds = auth_service.authenticate()
        self._service = build("webmasters", "v3", credentials=creds)

    @staticmethod
    def _create_request(
        start_date,
        end_date,
        dimensions,
        start_row,
        dimension_filter_groups=None,
        aggregation_type=None,
        data_type=None,
    ):
        request = {
            "startDate": start_date,
            "endDate": end_date,
            "dimensions": dimensions,
            "startRow": start_row,
            "rowLimit": GoogleSearchConsoleOperator.ROW_LIMIT,
        }

        if dimension_filter_groups:
            request["dimensionFilterGroups"] = dimension_filter_groups
        if aggregation_type:
            request["aggregationType"] = aggregation_type
        if data_type:
            request["type"] = data_type

        return request

    @retry(
        stop=stop_after_attempt(10),
        wait=wait_exponential(multiplier=1, max=60),
        retry=retry_if_exception_type(requests.exceptions.ReadTimeout),
    )
    def execute_request(self, site_url, request_body) -> list:
        try:
            response = self._service.searchanalytics().query(siteUrl=site_url, body=request_body).execute()
            logger.info("Search Analytics query executed successfully.")
            return response.get("rows", [])
        except Exception as e:
            logger.error(f"Error while executing Search Analytics query: {e}")
            raise GSCFetchError(f"Error while fetching GSC data: {e}")

    @staticmethod
    def _flatten_entry(dimensions, entry):
        flat_entry = {}
        for dim, value in zip(dimensions, entry["keys"]):
            flat_entry[dim] = value
        flat_entry.update(
            {
                "clicks": entry["clicks"],
                "impressions": entry["impressions"],
                "ctr": round(entry["ctr"], 2),
                "position": round(entry["position"], 1),
            }
        )
        return flat_entry

    def fetch_data(self, site_url, start_date: datetime.date, end_date: datetime.date, dimensions, required_columns=None) -> pd.DataFrame:
        if required_columns is None:
            required_columns = {"clicks", "impressions", "ctr", "position"}

        all_data = []
        start_row = 0

        while True:
            request_body = self._create_request(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                dimensions,
                start_row,
            )
            try:
                logger.info(f"Fetching GSC data from {start_date} to {end_date} for {site_url}, dimensions {dimensions}, start row {start_row}")
                data = self.execute_request(site_url, request_body)
            except GSCFetchError as e:
                logger.error(str(e))
                # If the error is 'user does not have access', return an empty DataFrame
                if "HttpError 403" in str(e):
                    logger.error("User does not have access.")
                    return pd.DataFrame()
                continue

            if not data:
                break

            flattened_data = [self._flatten_entry(dimensions, entry) for entry in data]
            all_data.extend(flattened_data)

            start_row += len(data)

        logger.info(f"Fetched {len(all_data)} rows of GSC data")
        df = pd.DataFrame(all_data)

        # Add missing columns with NaN values
        missing_columns = required_columns - set(df.columns)
        for column in missing_columns:
            df[column] = float("NaN")

        # Now, it's safe to cast types because all required columns are present
        return df.astype(
            {
                "clicks": "int64",
                "impressions": "int64",
                "ctr": "float64",
                "position": "float64",
            }
        )
