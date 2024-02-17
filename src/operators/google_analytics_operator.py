import logging

import pandas as pd
from googleapiclient.discovery import build

from operators.google_auth_operator import GoogleAuthOperator

logger = logging.getLogger(__name__)


class GoogleAnalyticsOperator:
    def __init__(self):
        self._service = None

    def set_credentials(self, auth_email: str) -> None:
        auth_service = GoogleAuthOperator(auth_email)
        creds = auth_service.authenticate()
        self._service = build("analyticsdata", "v1beta", credentials=creds)

    @staticmethod
    def _flatten_data(response: dict) -> pd.DataFrame:
        # Extract headers for DataFrame columns
        dimension_headers = [dh["name"] for dh in response["dimensionHeaders"]]
        metric_headers = [mh["name"] for mh in response["metricHeaders"]]
        columns = dimension_headers + metric_headers

        # Process each row of data
        data = []
        for row in response["rows"]:
            # Initialize a list to hold the values for this row
            row_data = []

            # Extract dimension values
            for dimension in row.get("dimensionValues", []):
                row_data.append(dimension.get("value"))

            # Extract metric values
            for metric in row.get("metricValues", []):
                row_data.append(metric.get("value"))

            data.append(row_data)

        df = pd.DataFrame(data, columns=columns)
        return df

    def fetch_data(self, ga_property_id, start_date, end_date, dimensions, metrics):
        dimension_names = [dim["name"] for dim in dimensions]
        metric_names = [metric["name"] for metric in metrics]
        logger.info(f"Fetching GA4 data for property {ga_property_id} from {start_date} to {end_date} with dimensions {dimension_names} and metrics {metric_names}")

        property_id = f"properties/{ga_property_id}"

        try:
            response = (
                self._service.properties()
                .runReport(
                    property=property_id,
                    body={
                        "date_ranges": [
                            {
                                "start_date": start_date.strftime("%Y-%m-%d"),
                                "end_date": end_date.strftime("%Y-%m-%d"),
                            }
                        ],
                        "dimensions": dimensions,
                        "metrics": metrics,
                    },
                )
                .execute()
            )
            logger.info("Data fetched successfully.")
            df = self._flatten_data(response)
            return df
        except Exception as e:
            logger.error(f"Failed to fetch GA4 data: {e}")
