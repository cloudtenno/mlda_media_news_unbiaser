import ollama
import re

class NewsSummarizer:
    def __init__(self, model='deepseek-r1:14b'):
        self.model = model
        self.summary = ""
        self.search_term = ""
    
    def read_news_article(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def generate_summary(self, news_content):
        prompt_summary = (
            f"Please read the following news article and provide a concise and clear summary. "
            f"\nSummary: <your summary here>\n\n"
            f"You MUST only start the summary after Summary:\n"
            f"News Article:\n{news_content}"
        )
        
        stream_summary = ollama.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt_summary}],
            stream=True,
        )
        
        summary_response = ""
        for chunk in stream_summary:
            summary_response += chunk['message']['content']
        
        last_think_index = summary_response.rfind("</think>")
        if last_think_index != -1:
            self.summary = summary_response[last_think_index + len("</think>"):].strip()
            self.summary = re.sub(r'^Summary:\s*', '', self.summary)
        else:
            self.summary = summary_response.strip()
        
        self.summary = re.sub(r'\*\*', '', self.summary)  # Remove all **
        
        with open('summary.txt', 'w', encoding='utf-8') as file:
            file.write(self.summary)
        
        return self.summary
    
    def generate_search_term(self):
        prompt_search = (
            f"Given the summary of this news article: {self.summary}, give me a very condensed single sentence summary of the article. "
            f"Output like this: Search Term: <condensed single sentence summary>\n\n"
            f'No bullet point is allowed, just a SINGLE CONDENSED SENTENCE.\n'
        )
        
        stream_search = ollama.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt_search}],
            stream=True,
        )
        
        search_response = ""
        for chunk in stream_search:
            search_response += chunk['message']['content']
        
        last_think_index = search_response.rfind("</think>")
        if last_think_index != -1:
            self.search_term = search_response[last_think_index + len("</think>"):].strip()
        else:
            self.search_term = search_response.strip()
        
        self.search_term = re.sub(r'\*\*', '', self.search_term)  # Remove all **
        
        with open('search_terms.txt', 'w', encoding='utf-8') as file:
            file.write(self.search_term)
        
        return self.search_term

if __name__ == "__main__":
    summarizer = NewsSummarizer()
    news_content = summarizer.read_news_article('initial.txt')
    summary = summarizer.generate_summary(news_content)
    print("\nExtracted Summary:")
    print(summary)
    
    search_term = summarizer.generate_search_term()
    print("\nSearch Term:")
    print(search_term)
