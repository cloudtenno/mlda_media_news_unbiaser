import ollama
import re
import glob
import os

class NewsArticleGenerator:
    def __init__(self, model='deepseek-r1:14b', directory='.'):
        """
        Initializes the NewsArticleGenerator class.
        :param model: The LLM model to use.
        :param directory: Directory to search for .txt files.
        """
        self.model = model
        self.directory = directory

    def _gather_news_content(self):
        """
        Reads and combines the contents of all .txt news files in the directory.
        :return: A formatted string containing all news articles with their sources.
        """
        file_paths = glob.glob(os.path.join(self.directory, '*.txt'))
        news_contents = ""
        
        for file_path in file_paths:
            domain = os.path.splitext(os.path.basename(file_path))[0]
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            news_contents += f"Source: {domain}\n{content}\n\n"
        
        return news_contents

    def generate_unbiased_article(self):
        """
        Generates an unbiased news article based on collected news sources.
        :return: The generated unbiased news article.
        """
        news_contents = self._gather_news_content()
        
        if not news_contents.strip():
            return "No news articles found in the directory."
        
        prompt_article = (
            "OUTPUT MUST BE IN ENGLISH "
            "You are given several news articles below, each prefixed with the source domain from which the news was scraped. "
            "Your task is to produce a single, unbiased news article that accurately reports what actually happened, using the details provided by each source. "
            "Please write the article in a proper narrative style without using any bullet points. "
            "Make sure to attribute or consider the context given by the source domains where applicable.\n\n"
            "News Articles:\n"
            f"{news_contents}"
        )
        
        stream_article = ollama.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt_article}],
            stream=True,
        )
        
        article_response = ""
        for chunk in stream_article:
            article_response += chunk['message']['content']
        
        return article_response

if __name__ == "__main__":
    generator = NewsArticleGenerator()
    article = generator.generate_unbiased_article()