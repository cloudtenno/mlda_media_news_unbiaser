from googlesearch import search
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import csv

class otherLanguageScrapper:
    def __init__(self, driver_path="C:\\Users\\luxin\\OneDrive\\Desktop\\LLM\\chromedriver.exe"):
        self.driver_path = driver_path
        self.headers = {
            "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/88.0.4324.150 Safari/537.36")
        }
        self.domain_count = {}
        self.csv_filename = "scraped_urls.csv"

    def save_url_to_csv(self, domain_raw, url):
        with open(self.csv_filename, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([domain_raw, url])
    
    def extract_text_from_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        paragraphs = soup.find_all('p')
        main_text = [p.get_text(strip=True) for p in paragraphs if not p.find_parent('a') and p.get_text(strip=True)]
        return "\n".join(main_text)
    
    def fetch_page_content(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            if response.status_code == 401:
                raise Exception("Unauthorized access with requests, falling back to Selenium.")
            return self.extract_text_from_html(response.text)
        except Exception as e:
            print(f"Requests failed with error: {e}. Falling back to Selenium...")
            return self.fetch_page_with_selenium(url)
    
    def fetch_page_with_selenium(self, url):
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
    
    def scrape_news(self, search_term, language):
        query = f'News {search_term}'
        results = list(search(query, num_results=5))
        
        if not results:
            print("No search results found. Exiting operation.")
            return
        
        for url in results:
            print(f"URL found: {url}")
            if not url.lower().startswith("http"):
                print(f"Skipping invalid URL: {url}")
                continue
            
            domain_raw = urlparse(url).netloc.replace("www.", "")
            if "wiki" in domain_raw.lower() or "sina" in domain_raw.lower() or "washingtonpost" in domain_raw.lower():
                print(f"Skipping URL from wiki domain: {url}")
                continue
            
            main_text_str = self.fetch_page_content(url)
            self.save_url_to_csv(domain_raw, url)
            
            domain_clean = domain_raw.replace(".com", "")
            self.domain_count[domain_clean] = self.domain_count.get(domain_clean, 0) + 1
            base_filename = f"{domain_clean}_{self.domain_count[domain_clean]}"
            raw_filename = f"{base_filename}_{language}_raw.txt"
            
            with open(raw_filename, "w", encoding="utf-8") as file:
                file.write(main_text_str)
            print(f"Saved raw {language} text to {raw_filename}")
    
    def scrape_chinese_news(self, chinese_search_term):
        self.scrape_news(chinese_search_term, "chinese")
    
    def scrape_japanese_news(self, japanese_search_term):
        self.scrape_news(japanese_search_term, "japanese")
    
    def scrape_hindi_news(self, hindi_search_term):
        self.scrape_news(hindi_search_term, "hindi")

# Example usage:
# scraper = NewsScraper()
# scraper.scrape_chinese_news(chinese_search_term)
# scraper.scrape_japanese_news(japanese_search_term)
# scraper.scrape_hindi_news(hindi_search_term)