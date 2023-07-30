import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize

def process_file(file_name):
    with open(file_name, "r", encoding='utf-8-sig') as file:
        text = file.read()
        lines = text.strip().split("\n")
        lines = [line.strip() for line in lines if line.strip()]
        text = " ".join(lines)
        sentences = sent_tokenize(text)
        return sentences