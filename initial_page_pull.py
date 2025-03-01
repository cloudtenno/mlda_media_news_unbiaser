import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

class WebScraper:
    def __init__(self, chromedriver_path=None):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        self.chromedriver_path = chromedriver_path

    def extract_text_from_html(self, html):
        """Extract text from <p> tags that are not inside <a> elements."""
        soup = BeautifulSoup(html, 'html.parser')
        paragraphs = soup.find_all('p')
        main_text = []
        for p in paragraphs:
            if not p.find_parent('a'):
                text = p.get_text(strip=True)
                if text:
                    main_text.append(text)
        return "\n".join(main_text)

    def fetch_with_requests(self, url):
        """Attempt to fetch the page using requests."""
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return self.extract_text_from_html(response.text)
            elif response.status_code == 401:
                raise Exception("Unauthorized access with requests.")
        except Exception as e:
            print(f"Requests failed with error: {e}")
        return None

    def fetch_with_selenium(self, url):
        """Fetch page content using Selenium as a fallback."""
        if not self.chromedriver_path:
            raise ValueError("Chromedriver path is required for Selenium scraping.")

        options = Options()
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service(self.chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        
        try:
            driver.get(url)
            time.sleep(3)  # Allow time for the page to load
            text_elements = driver.find_elements(By.XPATH, "//p[not(ancestor::a)]")
            main_text = [elem.text for elem in text_elements if elem.text.strip()]
            return "\n".join(main_text)
        finally:
            driver.quit()

    def scrape(self, url, use_selenium=False):
        """Scrape the given URL using requests or Selenium."""
        text = self.fetch_with_requests(url)
        if text is None and use_selenium:
            print("Falling back to Selenium...")
            text = self.fetch_with_selenium(url)
        return text

    def save_to_file(self, text, filename="initial.txt"):
        """Save extracted text to a file."""
        with open(filename, "w", encoding="utf-8") as file:
            file.write(text)
        print(f"Saved text to {filename}")

# Example usage:
# scraper = WebScraper(chromedriver_path="C:/Users/luxin/OneDrive/Desktop/LLM/chromedriver.exe")
# text = scraper.scrape("https://www.channelnewsasia.com/world/volodymyr-zelenskyy-donald-trump-shouting-match-ukraine-russia-4968516", use_selenium=True)
# scraper.save_to_file(text)