# News Scraper, Summarizer & Bias Analyzer

This repository contains a Flask web application that performs the following tasks:

- **Scrapes** a given news URL using both _requests_ and _Selenium_.
- **Summarizes** the scraped news article using a language model.
- **Generates search terms** based on the summary.
- **Scrapes additional news articles** (including Chinese, Japanese, and Hindi sources) using search queries.
- **Translates non-English articles** to English.
- **Generates an unbiased news article** from multiple sources.
- **Performs bias analysis** comparing media articles with the unbiased article using a language model via Ollama.

> **Note:** Our local weight model is trained and modified based on `deepseek-r1:14b` running on a machine equipped with an RTX4090. For quick testing or on laptops, you can pull the `deepseek-r1:1.5b` model, which is more lightweight and can run on less powerful hardware.

---

## Features

- **Web Scraping:** Uses the `requests` library and Selenium (with ChromeDriver) to extract news content.
- **News Summarization:** Uses a language model (via Ollama) to generate a concise summary and search term.
- **Multilingual News Scraping & Translation:** Scrapes news from non-English sources and translates them to English using [Deep Translator](https://pypi.org/project/deep-translator/).
- **Bias Analysis:** Compares translated media articles with an unbiased news article using the language model.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/news-scraper-summarizer.git
cd news-scraper-summarizer
```

### 2. Set Up a Virtual Environment

Create and activate a virtual environment:

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

Install the required packages by running your existing installation command (you already have the requirements.txt setup):

```bash
pip install -r requirements.txt
```

### 4. Install ChromeDriver for Selenium

- **Download:** Visit [ChromeDriver downloads](https://chromedriver.chromium.org/downloads) and choose the version compatible with your installed version of Chrome.
- **Place the Executable:** Either add the ChromeDriver executable to your system’s PATH or update the `chromedriver_path` parameter in the code with the full path to the executable.

### 5. Install Ollama and Pull the Model

#### Installing Ollama

Ollama is used to interact with the language model. To install Ollama:

- **Visit** the [Ollama website](https://ollama.ai) and download the installer for your operating system.
- **Follow** the provided installation instructions.

#### Pull the Appropriate Model

For **local high-performance usage**, our code is configured to work with `deepseek-r1:14b` (running on an RTX4090). However, for **quick testing or on a laptop**, you can pull the lightweight `deepseek-r1:1.5b` model by running:

```bash
ollama pull deepseek-r1:1.5b
```

This will download the lightweight version that is easier to run on less powerful hardware.

---

## Usage

1. **Start the Flask App:**

   ```bash
   python app.py
   ```

2. **Access the Application:**

   Open your browser and navigate to [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

3. **Scrape and Process News:**

   - Input a valid news URL.
   - The application will scrape the page, summarize the content, generate search terms, and save necessary data to files.
   - Endpoints are provided for additional news scraping (including multi-language scraping), translating articles, generating an unbiased article, and performing bias analysis.

4. **Background Processes:**

   Some tasks, such as scraping news for a given search term, run in the background using Python threads. Use the `/scraping_status` and `/get_news` endpoints for progress updates.

---

## Project Structure

- **app.py:** Main Flask application.
- **initial_page_pull.py:** Contains the `WebScraper` class for scraping web pages.
- **initial_news_processing.py:** Contains the `NewsSummarizer` class for summarization and generating search terms.
- **unbiaser.py:** Contains the `NewsArticleGenerator` class for generating an unbiased news article.
- **biasness_analysis.py:** Contains the `BiasAnalysis` class for performing bias analysis using Ollama.
- **news_search.py & translate_and_search.py:** Include classes for scraping news from search results and translating non-English news.
- **Other Files:** Various helper scripts for scraping, translating, and processing news data.

---

## License

[MIT License](LICENSE)

