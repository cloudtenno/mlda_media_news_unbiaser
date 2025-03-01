import os
import time
import chardet  # Install via: pip install chardet
from deep_translator import GoogleTranslator

class BaseTranslator:
    def __init__(self, source_language, target_language="en", max_retries=3, delay=0.05):
        self.source_language = source_language
        self.target_language = target_language
        self.max_retries = max_retries
        self.delay = delay
    
    def detect_encoding(self, filepath):
        """Detect the file encoding to avoid garbled text."""
        with open(filepath, 'rb') as f:
            raw_data = f.read(50000)  # Read a small chunk to detect encoding
        result = chardet.detect(raw_data)
        return result['encoding'] if result['encoding'] else 'utf-8'  # Default to utf-8 if unsure

    def translate_line(self, line):
        retries = 0
        while retries < self.max_retries:
            try:
                return GoogleTranslator(source=self.source_language, target=self.target_language).translate(line.strip())
            except Exception as e:
                retries += 1
                print(f"Retrying ({retries}/{self.max_retries}) for line: {line[:30]}... - {e}")
                time.sleep(10)
        print(f"Failed to translate after {self.max_retries} retries: {line[:30]}...")
        return line  # Return original line if translation fails
    
    def translate_file(self, input_filepath, output_filepath):
        try:
            # Detect encoding
            encoding = self.detect_encoding(input_filepath)
            print(f"Detected encoding for {input_filepath}: {encoding}")

            # Read the file with the correct encoding
            with open(input_filepath, 'r', encoding=encoding, errors='replace') as file:
                lines = file.readlines()

            # Translate only readable lines (skip scrambled code)
            translated_lines = [self.translate_line(line) if line.strip() else line for line in lines]

            # Save translated content
            with open(output_filepath, 'w', encoding='utf-8') as file:
                file.write("\n".join(translated_lines))

            print(f"Translated: {input_filepath} -> {output_filepath}")

            os.remove(input_filepath)
            print(f"Deleted raw file: {input_filepath}")

        except Exception as e:
            print(f"Error translating {input_filepath}: {e}")
    
    def batch_translate(self, directory, raw_suffix, translated_suffix):
        for filename in os.listdir(directory):
            if filename.endswith(raw_suffix):
                input_filepath = os.path.join(directory, filename)
                output_filepath = os.path.join(directory, filename.replace(raw_suffix, translated_suffix))
                self.translate_file(input_filepath, output_filepath)

class ChineseToEnglishTranslator(BaseTranslator):
    def __init__(self):
        super().__init__(source_language="zh-CN")
    
    def batch_translate(self, directory):
        super().batch_translate(directory, "_chinese_raw.txt", "_chinese_translated.txt")

class JapaneseToEnglishTranslator(BaseTranslator):
    def __init__(self):
        super().__init__(source_language="ja")
    
    def batch_translate(self, directory):
        super().batch_translate(directory, "_japanese_raw.txt", "_japanese_translated.txt")

class HindiToEnglishTranslator(BaseTranslator):
    def __init__(self):
        super().__init__(source_language="hi")
    
    def batch_translate(self, directory):
        super().batch_translate(directory, "_hindi_raw.txt", "_hindi_translated.txt")

if __name__ == "__main__":
    directory = os.getcwd()
    
    chinese_translator = ChineseToEnglishTranslator()
    chinese_translator.batch_translate(directory)
    
    japanese_translator = JapaneseToEnglishTranslator()
    japanese_translator.batch_translate(directory)
    
    hindi_translator = HindiToEnglishTranslator()
    hindi_translator.batch_translate(directory)
