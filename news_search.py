import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
import csv
from googlesearch import search
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

class NewsScraper:
    def __init__(self, driver_path):
        self.driver_path = driver_path
        self.headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/88.0.4324.150 Safari/537.36")
        }
        self.domain_count = {}
        self.csv_filename = "scraped_urls.csv"
        
        # Create CSV file with header if not exists
        with open(self.csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Domain", "URL"])
        
    def get_search_results(self, search_term, num_results=15):
        query = f'News {search_term}'
        return list(search(query, num_results=num_results))
    
    @staticmethod
    def extract_text_from_html(html):
        soup = BeautifulSoup(html, 'html.parser')
        paragraphs = soup.find_all('p')
        main_text = []
        for p in paragraphs:
            if not p.find_parent('a'):
                text = p.get_text(strip=True)
                if text:
                    main_text.append(text)
        return "\n".join(main_text)
    
    def fetch_page_content(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            if response.status_code == 401:
                raise Exception("Unauthorized access with requests, falling back to Selenium.")
            return self.extract_text_from_html(response.text)
        except Exception as e:
            print(f"Requests failed with error: {e}. Falling back to Selenium...")
            return self.fetch_with_selenium(url)
    
    def fetch_with_selenium(self, url):
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        service = Service(self.driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_page_load_timeout(60)
        
        try:
            driver.get(url)
            time.sleep(3)
            text_elements = driver.find_elements(By.XPATH, "//p[not(ancestor::a)]")
            main_text = [elem.text for elem in text_elements if elem.text.strip()]
            return "\n".join(main_text)
        except TimeoutException:
            print("Selenium timed out after 60 seconds trying to load the page. Skipping this URL.")
            return ""
        finally:
            driver.quit()
    
    def save_text_to_file(self, text, domain_raw):
        domain_clean = domain_raw.replace(".com", "").replace("www.", "")
        if domain_clean in self.domain_count:
            self.domain_count[domain_clean] += 1
            filename = f"{domain_clean}_{self.domain_count[domain_clean]}.txt"
        else:
            self.domain_count[domain_clean] = 0
            filename = f"{domain_clean}.txt"
        
        with open(filename, "w", encoding="utf-8") as file:
            file.write(text)
        
        print(f"Saved text to {filename}")
    
    def save_url_to_csv(self, domain_raw, url):
        with open(self.csv_filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([domain_raw, url])
    
    def scrape_news(self, search_term):
        results = self.get_search_results(search_term)
        if not results:
            print("No search results found. Exiting operation.")
            return
        
        for url in results:
            print(f"URL found: {url}")
            
            if not url.lower().startswith("http"):
                print(f"Skipping invalid URL: {url}")
                continue
            
            domain_raw = urlparse(url).netloc
            if "wiki" in domain_raw.lower() or "washingtonpost" in domain_raw.lower():
                print(f"Skipping URL domain: {url}")
                continue
            
            main_text_str = self.fetch_page_content(url)
            if main_text_str:
                self.save_text_to_file(main_text_str, domain_raw)
                self.save_url_to_csv(domain_raw, url)

# Example usage:
# scraper = NewsScraper(r"C:\\path\\to\\chromedriver.exe")
# scraper.scrape_news("AI advancements")