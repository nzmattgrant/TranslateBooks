import requests
import pickle
from Configuration import DEEPL_API_KEY
from HumanTranslationMatching import process_file
import spacy
import os
import spacy_transformers

nlp = spacy.load('de_dep_news_trf')

def update_deepl_translation_dict_from_file(filename):
    translation_dict = {}
    translation_dict_path = "traslation_dict.pkl"
    if os.path.isfile(translation_dict_path):
        with open(translation_dict_path, "rb") as f:
            translation_dict = pickle.load(f)[0]

    sentences = process_file(filename)

    url = 'https://api-free.deepl.com/v2/translate'
    auth_key = DEEPL_API_KEY
    target_lang = 'EN'
    source_lang = 'DE'

    data = {
        'text': '',
        'target_lang': target_lang,
        'source_lang': source_lang
    }

    headers = {
        'Authorization': 'DeepL-Auth-Key ' + auth_key,
    }

    for sentence in sentences:
        tokens = nlp(sentence)
        for token in tokens:
            if token.is_punct or token.text in translation_dict:
                #word already in dict or is puctuation
                continue
            print("adding new word", token.text)
            try:
                data["text"] = token.text
                response = requests.post(url, data=data, headers=headers)

                if response.ok:
                    json_data = response.json()
                    translated_text = json_data['translations'][0]['text']
                    dict[token.text] = translated_text
                else:
                    print('Error:', response.status_code, response.reason)
            except Exception as e:
                print("exception occured", e)
                continue

    with open("traslation_dict.pkl", "wb") as f:
        pickle.dump(translation_dict, f)

update_deepl_translation_dict_from_file("Hänsel und Gretel.txt")