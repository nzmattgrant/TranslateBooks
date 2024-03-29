from flask import Flask, jsonify, request, send_file
import os
import pandas as pd
from flask_cors import CORS
import pickle
import requests
from configuration import HUGGING_FACE_API_KEY
import difflib


def calculate_similarity(original_sentence, sentence_to_compare):
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    output = query({
        "inputs": {
            "source_sentence": original_sentence,
            "sentences": [
                sentence_to_compare,
                sentence_to_compare
            ]
        },
    })
    return output


file_name = 'matched_deepl_translations_multiple_books.pkl'
matched_translations = pd.read_pickle(file_name)

translation_dict = {}

with open("translation_dict.pkl", "rb") as f:
    translation_dict = pickle.load(f)

german_token_dicts = {}

with open("german_token_dicts.pkl", "rb") as f:
    german_token_dicts = pickle.load(f)

app = Flask(__name__, static_folder='dist')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/')
def index_client():
    dist_dir = os.path.dirname(__file__)
    entry = os.path.join(os.path.join(dist_dir, 'dist'), 'index.html')
    return send_file(entry)


@app.route("/api/sentences", methods=['GET'])
def get_sentence2():
    args = request.args
    book_id = int(args['id'])-1  # zero indexed
    line_num = int(args['lineNumber'])
    row = german_token_dicts[book_id][line_num]
    presentation_sentence_tokens_with_definition = []
    for token_info in row:
        token = token_info["word"]
        if token_info["function"] == "punctuation" and len(presentation_sentence_tokens_with_definition) > 0:
            presentation_sentence_tokens_with_definition[-1]["display"] += token
            continue
        last_token_info = {
            "word": token,
            "display": token,
            "lemma": token_info["lemma"],
            "definition": {
                "link": f"https://www.deepl.com/translator#de/en/{token}",
                "function": token_info["function"],
                "description": translation_dict[token]
            }
        }
        presentation_sentence_tokens_with_definition.append(last_token_info)
    first_sentence = row = matched_translations[book_id][line_num]["german_sentence"]
    second_sentence = row = matched_translations[book_id][line_num]["english_machine_translation"]

    return jsonify({
        "sentence": first_sentence,
        "presentation_sentence_tokens": presentation_sentence_tokens_with_definition,
        "translation": second_sentence
    })


@app.route("/api/similarity", methods=['POST'])
def check_similarity():
    data = request.get_json()
    sentence1 = data["sentence1"]
    sentence2 = data["sentence2"]
    result = calculate_similarity(sentence1, sentence2)
    diff = difflib.ndiff(sentence1, sentence2)
    print(result)
    return {"similarity": result[0], "diff": list(diff)}


@app.route("/api/books", methods=['GET'])
def book_info():
   return [
    {
       "id": 1,
       "title": "The Metamorphosis",
       "author": "Franz Kafka",
       "numberOfSentences": len(matched_translations[0]),
       "slug": "the-metamorphosis"
    },
    {
       "id": 2,
       "title": "Hansel and Gretel",
       "author": "The Brothers Grimm",
       "numberOfSentences": len(matched_translations[1]),
       "slug": "hansel-and-gretel"
    },
    {
       "id": 3,
       "title": "Snow White",
       "author": "The Brothers Grimm",
       "numberOfSentences": len(matched_translations[2]),
       "slug": "snow-white"
    },
    # {
    #    "id": 4,
    #    "title": "Thus spake Zarathustra",
    #    "author": "Friedrich Nietzsche",
    #    "numberOfSentences": 0,
    #    "slug": "thus-spake-zarathustra"
    # }
    ]


@app.route("/api/solution", methods=['GET'])
def get_solution():
   return


@app.route('/<path:path>')
def static_proxy(path):
    return app.send_static_file(path)


if __name__ == "__main__":
  app.run()
