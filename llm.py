import ollama

# Path to the document containing the news article (e.g., 'news.txt')
document_path1 = 'news.txt'

# Read the document content
with open(document_path1, 'r', encoding='utf-8') as file:
    news_content1 = file.read()

# Prepare the prompt for summarization and search terms
prompt1 = f"Summarize this news and give me search terms to search for the same news from other news agencies:\n\n{news_content1}\n\nOutput in format:\n\nSearch terms: <search terms>\n\nSummary: <summary>"

# Send the request to the model and stream the response
stream1 = ollama.chat(
    model='deepseek-r1:14b',
    messages=[{'role': 'user', 'content': prompt1}],
    stream=True,
)

# Collect the summary and search terms
summary_and_terms = ""
for chunk in stream1:
    content = chunk['message']['content']
    print(content, end='', flush=True)
    summary_and_terms += content

# Extract search terms and summary
search_terms_start = summary_and_terms.find("Search terms:") + len("Search terms:")
summary_start = summary_and_terms.find("Summary:")

search_terms = summary_and_terms[search_terms_start:summary_start].strip()
summary = summary_and_terms[summary_start + len("Summary:"):].strip()

# Prepare the second prompt to refine search queries
prompt2 = f"Based on the summary and search terms provided, generate a single specific keyword phrases that can be typed into a search engine to find similar news. Make them concise and effective for retrieving relevant news articles.\n\nSearch terms: {search_terms}\n\nSummary: {summary}\n\nOutput format:\n\nRefined search queries: <search queries>"

# Send the request to the model for refined search queries
stream2 = ollama.chat(
    model='deepseek-r1:14b',
    messages=[{'role': 'user', 'content': prompt2}],
    stream=True,
)

# Output the refined search queries
for chunk in stream2:
    print(chunk['message']['content'], end='', flush=True)
