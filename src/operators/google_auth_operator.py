import logging
import os
import pickle
import webbrowser

from django.conf import settings
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

logger = logging.getLogger(__name__)


class GoogleAuthOperator:
    def __init__(self, auth_email):
        self.auth_email = auth_email
        self.token_file_path = os.path.abspath(os.path.join(settings.SECRETS_DIR, f"{self.auth_email}.token.pickle"))

    # Constants
    CLIENT_SECRET_FILE = os.path.abspath(os.path.join(settings.SECRETS_DIR, "client_secret.json"))
    GOOGLE_DEV_CONSOLE_URL = "https://console.developers.google.com/"

    SCOPES = [
        "https://www.googleapis.com/auth/webmasters.readonly",
        "https://www.googleapis.com/auth/analytics.readonly",
    ]

    def authenticate(self):
        creds = self.__get_credentials(self.token_file_path)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing Google auth credentials")
                creds.refresh(Request())
            elif os.path.exists(self.CLIENT_SECRET_FILE):
                logger.info("Getting new Google auth credentials")
                flow = InstalledAppFlow.from_client_secrets_file(self.CLIENT_SECRET_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                logger.error("client_secret.json not found. Please login to Google Dev Console and download it.")
                webbrowser.open(self.GOOGLE_DEV_CONSOLE_URL)
                return None

            self.__save_credentials(creds, self.token_file_path)
            logger.info("Google auth credentials saved")

        return creds

    @staticmethod
    def __get_credentials(token_file):
        if os.path.exists(token_file):
            with open(token_file, "rb") as f:
                return pickle.load(f)
        return None

    @staticmethod
    def __save_credentials(creds, token_file):
        logger.info(f"Saving credentials to {token_file}")
        with open(token_file, "wb") as f:
            pickle.dump(creds, f)
