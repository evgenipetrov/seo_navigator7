from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager


class BrowserOperator:
    def __init__(self):
        options = Options()
        options.add_argument("--headless")  # Ensure GUI is off
        options.add_argument("--disable-cache")  # Disable caching
        # Initialize the WebDriver with ChromeDriverManager
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=options)

    def get_page_contents(self, url: str) -> str:
        """
        Navigate to a URL and return the page contents.

        :param url: The URL to navigate to.
        :return: The page contents as a string.
        """
        self.driver.get(url)
        return self.driver.page_source

    def close_browser(self):
        """Close the browser and clean up resources."""
        self.driver.quit()
