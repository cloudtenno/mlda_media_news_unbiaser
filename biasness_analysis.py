import glob
import os
import ollama

class BiasAnalysis:
    def __init__(self, unbiased_article, directory="."):
        """
        Initialize the BiasAnalysis class.

        :param unbiased_article: The unbiased news article (string) to compare against.
        :param directory: The directory where the translated files are located.
        """
        self.unbiased_article = unbiased_article
        self.directory = directory

    def load_media_articles(self, language: str) -> str:
        """
        Load media articles translated into a specific language.

        :param language: The language identifier in lowercase (e.g., 'chinese', 'japanese', 'hindi').
        :return: A concatenated string of all media articles with a header per source.
        """
        # Build the file pattern based on language.
        pattern = os.path.join(self.directory, f"*_{language}_translated.txt")
        files = glob.glob(pattern)
        contents = ""
        for file_path in files:
            domain = os.path.splitext(os.path.basename(file_path))[0]
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            contents += f"Source: {domain}\n{content}\n\n"
        return contents

    def _analyze_bias(self, language: str, language_label: str) -> str:
        """
        Internal method to perform bias analysis for a given language.

        :param language: Language string used in file naming (e.g., 'chinese').
        :param language_label: Human-readable label for the prompt (e.g., 'Chinese').
        :return: The bias analysis result as a string.
        """
        media_articles = self.load_media_articles(language)
        prompt = (
            f"You are provided with two texts: one is a collection of {language_label} media news articles, "
            "and the other is an unbiased news article generated by combining multiple sources. "
            "Please analyze the differences between the two texts in terms of tone, framing, emphasis, and any signs of bias. "
            "Write your analysis as a coherent narrative without bullet points.\n\n"
            f"{language_label} Media Articles:\n{media_articles}\n\n"
            f"Unbiased News Article:\n{self.unbiased_article}\n\n"
            "I do not need summary of the article, I need the bias analysis of the article."
        )

        stream = ollama.chat(
            model='deepseek-r1:14b',
            messages=[{'role': 'user', 'content': prompt}],
            stream=True,
        )
        analysis_response = ""
        for chunk in stream:
            # Streaming output to the console as it arrives.
            print(chunk['message']['content'], end='', flush=True)
            analysis_response += chunk['message']['content']
        return analysis_response

    def chinese_biasness_analysis(self) -> str:
        """
        Perform bias analysis for Chinese media articles.
        
        :return: The bias analysis result as a string.
        """
        return self._analyze_bias(language="chinese", language_label="Chinese")

    def japanese_biasness_analysis(self) -> str:
        """
        Perform bias analysis for Japanese media articles.
        
        :return: The bias analysis result as a string.
        """
        return self._analyze_bias(language="japanese", language_label="Japanese")

    def Hindi_biasness_analysis(self) -> str:
        """
        Perform bias analysis for Hindi media articles.
        
        :return: The bias analysis result as a string.
        """
        # Note: Although method names are typically lowercase in Python,
        # this method name is kept as provided.
        return self._analyze_bias(language="hindi", language_label="Hindi")

# -------------------------------
# Example usage:
# -------------------------------

# Assume 'processed_article' is your unbiased news article generated from another part of your code.
processed_article = "This is an example unbiased news article generated from multiple sources."

# Create an instance of the BiasAnalysis class.
bias_analyzer = BiasAnalysis(unbiased_article=processed_article)

# Call any of the analysis methods.
print("\n\nChinese Bias Analysis:")
chinese_analysis = bias_analyzer.chinese_biasness_analysis()

print("\n\nJapanese Bias Analysis:")
japanese_analysis = bias_analyzer.japanese_biasness_analysis()

print("\n\nHindi Bias Analysis:")
hindi_analysis = bias_analyzer.Hindi_biasness_analysis()
