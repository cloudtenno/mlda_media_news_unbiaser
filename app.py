from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
import validators
import threading
import csv
import os
import glob
from initial_page_pull import WebScraper
from initial_news_processing import NewsSummarizer

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key or load from an environment variable

# Global flag to track scraping status.
scraping_complete = False

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    # Remove all .txt files in the current directory
    txt_files = glob.glob("*.txt")
    for txt_file in txt_files:
        os.remove(txt_file)
        print(f"Removed {txt_file}")
    # Remove all .csv files in the current directory
    csv_files = glob.glob("*.csv")
    for csv_file in csv_files:
        os.remove(csv_file)
        print(f"Removed {csv_file}")
    print("All .txt and .csv files have been removed.")
    
    url = request.form.get('url')
    if not validators.url(url):
        flash('Please enter a valid URL.')
        return redirect(url_for('index'))
    try:
        scraper = WebScraper(chromedriver_path="C:/Users/luxin/OneDrive/Desktop/LLM/chromedriver.exe")
        text = scraper.scrape(url, use_selenium=True)
        scraper.save_to_file(text)
    except Exception as e:
        flash(f'Error during scraping: {str(e)}')
        return redirect(url_for('index'))
    try:
        summarizer = NewsSummarizer()
        news_content = summarizer.read_news_article('initial.txt')
        summary = summarizer.generate_summary(news_content)
        search_term = summarizer.generate_search_term()
    except Exception as e:
        flash(f'Error during summarization: {str(e)}')
        return redirect(url_for('index'))
    session['search_term'] = search_term
    return render_template('results.html', summary=summary, search_term=search_term)

@app.route('/run_scraper', methods=['POST'])
def run_scraper():
    search_term = request.form.get('search_term')
    if not search_term:
        return jsonify({'error': 'No search term provided.'}), 400
    session['search_term'] = search_term
    global scraping_complete
    scraping_complete = False  # Reset flag before starting.

    def run_scraper_in_background(search_term):
         from news_search import NewsScraper
         scraper = NewsScraper(r"C:\Users\luxin\OneDrive\Desktop\LLM\chromedriver.exe")
         scraper.scrape_news(search_term)
         global scraping_complete
         scraping_complete = True  # Mark as finished.

    thread = threading.Thread(target=run_scraper_in_background, args=(search_term,))
    thread.start()
    return jsonify({'status': 'started'})

@app.route('/get_news', methods=['GET'])
def get_news():
    csv_file = 'scraped_urls.csv'
    results = []
    if os.path.exists(csv_file):
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(row)
    return jsonify(results)

# New endpoint to check if scraping is finished.
@app.route('/scraping_status', methods=['GET'])
def scraping_status():
    global scraping_complete
    return jsonify({'complete': scraping_complete})

@app.route('/news_results', methods=['GET'])
def news_results():
    return render_template('news_results.html')

@app.route('/translate_news/<language>', methods=['POST'])
def translate_news(language):
    search_term = session.get('search_term')
    if not search_term:
        return jsonify({'error': 'Search term not found in session.'}), 400
    try:
        from deep_translator import GoogleTranslator
        from translate_and_search import otherLanguageScrapper
        scraper = otherLanguageScrapper()
        import os
        directory = 'c:\\Users\\luxin\\OneDrive\\Desktop\\LLM'
        os.chdir(directory)
        if language.lower() == "chinese":
            # Translate before scraping
            chinese_search_term = GoogleTranslator(source='en', target='zh-CN').translate(search_term)
            scraper.scrape_chinese_news(chinese_search_term)
            from translate_news_to_english import ChineseToEnglishTranslator
            chinese_translator = ChineseToEnglishTranslator()
            chinese_translator.batch_translate(directory)
        elif language.lower() == "japanese":
            japanese_search_term = GoogleTranslator(source='en', target='ja').translate(search_term)
            scraper.scrape_japanese_news(japanese_search_term)
            from translate_news_to_english import JapaneseToEnglishTranslator
            japanese_translator = JapaneseToEnglishTranslator()
            japanese_translator.batch_translate(directory)
        elif language.lower() == "indian":
            hindi_Search_term = GoogleTranslator(source='en', target='hi').translate(search_term)
            scraper.scrape_hindi_news(hindi_Search_term)
            from translate_news_to_english import HindiToEnglishTranslator
            hindi_translator = HindiToEnglishTranslator()
            hindi_translator.batch_translate(directory)
        else:
            return jsonify({'error': 'Unsupported language.'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'status': 'completed'})

@app.route('/generate_unbiased', methods=['POST'])
def generate_unbiased():
    try:
        from unbiaser import NewsArticleGenerator
        generator = NewsArticleGenerator()
        article = generator.generate_unbiased_article()
        last_think_index = article.rfind("</think>")
        if last_think_index != -1:
            processed_article = article[last_think_index + len("</think>"):].strip()
        else:
            processed_article = article.strip()
        # Save the processed article for bias analysis.
        session['processed_article'] = processed_article
    except Exception as e:
        processed_article = "Error generating unbiased article: " + str(e)
    return render_template('unbiased_news.html', article=processed_article)

@app.route('/bias_analysis/<language>', methods=['GET'])
def bias_analysis(language):
    processed_article = session.get('processed_article')
    if not processed_article:
        return jsonify({'error': 'Processed article not found'}), 400
    from biasness_analysis import BiasAnalysis
    bias_analyzer = BiasAnalysis(unbiased_article=processed_article)
    result = ""
    if language.lower() == "chinese":
        if glob.glob('*_chinese_translated.txt'):
            result = bias_analyzer.chinese_biasness_analysis()
            result = result.split("</think>")[-1].strip()
        else:
            result = "No Chinese media articles found; skipping Chinese analysis."
    elif language.lower() == "japanese":
        if glob.glob('*_japanese_translated.txt'):
            result = bias_analyzer.japanese_biasness_analysis()
            result = result.split("</think>")[-1].strip()
        else:
            result = "No Japanese media articles found; skipping Japanese analysis."
    elif language.lower() == "hindi":
        if glob.glob('*_hindi_translated.txt'):
            result = bias_analyzer.Hindi_biasness_analysis()
            result = result.split("</think>")[-1].strip()
        else:
            result = "No Hindi media articles found; skipping Hindi analysis."
    else:
        return jsonify({'error': 'Unsupported language'}), 400
    return jsonify({'analysis': result})

if __name__ == '__main__':
    app.run(debug=True)
