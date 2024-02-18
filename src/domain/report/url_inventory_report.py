import logging

import pandas as pd

from domain.report.base_report import BaseReport
from model.core.project.models import ProjectModel
from model.core.url.models import UrlModelManager
from model.report.url_inventory_report.models import UrlInventoryReportModelManager, UrlInventoryReportModel

logger = logging.getLogger(__name__)


class UrlInventoryReport(BaseReport):
    _REPORT_NAME = "url_inventory_report"

    def __init__(self, project: ProjectModel):
        super().__init__(project)
        self.url_inventory = None

    @property
    def report_name(self) -> str:
        return self._REPORT_NAME

    @property
    def model_class(self) -> UrlInventoryReportModel:
        return UrlInventoryReportModel

    def _collect_data(self) -> None:
        self._export_data["semrush_analytics_organic_pages_domain"] = self.export_manager.get_data("semrush_analytics_organic_pages_domain")
        self._export_data["semrush_analytics_organic_positions_domain"] = self.export_manager.get_data("semrush_analytics_organic_positions_domain")
        self._export_data["semrush_analytics_backlinks_backlinks_domain"] = self.export_manager.get_data("semrush_analytics_backlinks_backlinks_domain")
        self._export_data["screamingfrog_spider_crawl_export"] = self.export_manager.get_data("screamingfrog_spider_crawl_export")
        self._export_data["screamingfrog_sitemap_crawl_export"] = self.export_manager.get_data("screamingfrog_sitemap_crawl_export")
        self._export_data["googleanalytics_months_14_to_0_export"] = self.export_manager.get_data("googleanalytics_months_14_to_0_export")
        self._export_data["googleasearchconsole_page_months_16_to_0_export"] = self.export_manager.get_data("googleasearchconsole_page_months_16_to_0_export")

    def _prepare_data(self) -> None:
        urls = []
        urls.extend(self._export_data["semrush_analytics_organic_pages_domain"]["URL"].tolist())
        urls.extend(self._export_data["semrush_analytics_organic_positions_domain"]["URL"].tolist())
        urls.extend(self._export_data["semrush_analytics_backlinks_backlinks_domain"]["Target url"].tolist())
        urls.extend(self._export_data["screamingfrog_spider_crawl_export"]["Address"].tolist())
        urls.extend(self._export_data["screamingfrog_sitemap_crawl_export"]["Address"].tolist())
        urls.extend(self._export_data["googleanalytics_months_14_to_0_export"]["FULL_ADDRESS"].tolist())
        urls.extend(self._export_data["googleasearchconsole_page_months_16_to_0_export"]["page"].tolist())
        # prepare for final list crawl
        unique_urls = list(set(urls))
        unique_urls = [url for url in unique_urls if not UrlModelManager.is_fragmented(url)]  # drop fragmented urls
        self._export_data["screamingfrog_list_crawl_export"] = self.export_manager.get_data("screamingfrog_list_crawl_export", urls=unique_urls)
        # collect list crawl data
        urls.extend(self._export_data["screamingfrog_list_crawl_export"]["Address"].tolist())
        # set report base
        unique_urls = list(set(urls))
        unique_urls = [url for url in unique_urls if not UrlModelManager.is_fragmented(url)]  # drop fragmented urls
        # Initialize _report_base DataFrame with columns from UrlInventoryReportModel
        model_fields = self.model_class.objects.get_field_names()  # Use your method to get field names
        model_fields.append("BASE_URL")  # Add BASE_URL to the list of columns
        self._report_base = pd.DataFrame(columns=model_fields)

        # Populate BASE_URL column with unique URLs
        self._report_base["BASE_URL"] = pd.Series(unique_urls)
        self._export_data["url_inventory_report"] = self.export_manager.get_data("url_inventory_report", urls=unique_urls)

    def _process_data(self) -> None:
        # Perform the initial merge
        self._report_data = self._report_base.merge(self._export_data["url_inventory_report"], left_on="BASE_URL", right_on="request_url", how="left")

        # Prepare the DataFrame from 'url_inventory_report' for update by setting its index to 'request_url'
        update_df = self._export_data["url_inventory_report"].set_index("request_url")

        # Update '_report_data' by overwriting values with those from 'update_df' wherever columns and indices match
        # Ensure '_report_data' index is set to 'BASE_URL' for proper alignment during update
        self._report_data.set_index("BASE_URL", inplace=True)
        self._report_data.update(update_df)

        # Optionally, reset the index if you want 'BASE_URL' back as a column
        self._report_data.reset_index(inplace=True)

    def _finalize(self) -> None:
        # Drop all columns that start with "BASE_"
        base_columns = [col for col in self._report_data.columns if col.startswith("BASE_")]
        self._report_data.drop(columns=base_columns, inplace=True)

    def _update_db(self) -> None:
        for index, row in self._report_data.iterrows():
            arguments = row.to_dict()
            arguments["project"] = self.project
            UrlInventoryReportModelManager.push(**arguments)

    # def _pull_updates_from_excel(self) -> None:
    #     excel_data = self._excel_operator.pull_updates(self.report_name)
    #     fk_fields = self.model_class.objects.get_foreign_key_fields()
    #
    #     for index, row in excel_data.iterrows():
    #         query_kwargs = {}
    #         update_fields = {}
    #
    #         for field, value in row.items():
    #             # Check if field is a foreign key that needs to be resolved
    #             if field in fk_fields:
    #                 related_model = fk_fields[field]
    #                 related_model_manager = related_model.objects
    #
    #                 # Assume get_instance_id is available on the manager
    #                 fk_id = related_model_manager.get_instance_id(str(value))
    #                 if fk_id is not None:
    #                     query_kwargs[field + "_id"] = fk_id  # Use the foreign key field with _id suffix for filtering
    #                 else:
    #                     logger.warning(f"Could not find related instance for field '{field}' with value '{value}'")
    #                     break  # Skip this row if any foreign key resolution fails
    #             else:
    #                 # For non-foreign key fields, prepare for direct update
    #                 update_fields[field] = value
    #
    #         else:  # This else clause runs if no break occurs in the loop
    #             db_entry = self.model_class.objects.filter(**query_kwargs).first()
    #             if db_entry:
    #                 for field, value in update_fields.items():
    #                     setattr(db_entry, field, value)
    #                 db_entry.save()
    #                 logger.info(f"Updated database entry for {query_kwargs}")
    #             else:
    #                 # Handle the case where the entry doesn't exist; you might want to create a new instance
    #                 logger.info(f"No entry found matching {query_kwargs}, consider creating a new instance")

    # def _pull_updates_from_excel(self) -> None:
    #     excel_data = self._excel_operator.pull_updates(self.report_name)
    #     unique_together_fields = self.model_class.IDENTIFYING_FIELDS
    #     excel_data["unique_together"] = excel_data[unique_together_fields].apply(tuple, axis=1)
    #
    #     fk_mapping = {
    #         "project": "project__name",
    #         "request_url": "request_url__full_address",
    #     }
    #
    #     for index, row in excel_data.iterrows():
    #         unique_together_values = list(row["unique_together"])
    #
    #         for i, field in enumerate(unique_together_fields):
    #             if field in fk_mapping:
    #                 lookup_field = fk_mapping[field]
    #                 lookup_result = self.model_class.objects.filter(**{lookup_field: unique_together_values[i]}).first()
    #                 if lookup_result is None:
    #                     logger.warning(f"Lookup failed for field '{field}' with value '{unique_together_values[i]}'. Skipping row.")
    #                     break  # Skip this row if any lookup fails
    #                 unique_together_values[i] = lookup_result.id
    #         else:  # This else executes if the loop completes without hitting 'break'
    #             db_entry = self.model_class.objects.filter(**dict(zip(unique_together_fields, unique_together_values))).first()
    #
    #             if db_entry:
    #                 for field in self.model_class.MANUAL_FIELDS:
    #                     if field in row:
    #                         logging.debug(f"Before updating: {row}")
    #                         logging.debug(f"Before updating: {field} = {getattr(db_entry, field)}")
    #                         setattr(db_entry, field, row[field])
    #                         logging.debug(f"After updating: {field} = {getattr(db_entry, field)}")
    #                 db_entry.save()
