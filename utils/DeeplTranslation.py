import requests
import pickle
from Configuration import DEEPL_API_KEY
import spacy
import os
from Shared import process_file

nlp = spacy.load('de_dep_news_trf')

def translate_wtih_deepl(text):
    url = 'https://api-free.deepl.com/v2/translate'
    auth_key = DEEPL_API_KEY
    target_lang = 'EN'
    source_lang = 'DE'

    data = {
        'text': text,
        'target_lang': target_lang,
        'source_lang': source_lang
    }

    headers = {
        'Authorization': 'DeepL-Auth-Key ' + auth_key,
    }

    try:
        response = requests.post(url, data=data, headers=headers)

        if response.ok:
            json_data = response.json()
            translated_text = json_data['translations'][0]['text']
            return translated_text
        else:
            print('Error:', response.status_code, response.reason)
            return None
    except Exception as e:
        print("exception occured", e)
        return None

def update_deepl_translation_dict_from_file(german_sentences):
    translation_dict = {}
    translation_dict_path = "translation_dict.pkl"
    if os.path.isfile(translation_dict_path):
        with open(translation_dict_path, "rb") as f:
            translation_dict = pickle.load(f)

    for sentence in german_sentences:
        tokens = nlp(sentence)
        for token in tokens:
            if token.is_punct or token.text in translation_dict:
                #word already in dict or is puctuation
                continue
            print("adding new word", token.text)
            translated_text = translate_wtih_deepl(token.text)
            if translated_text is None:
                continue
            translation_dict[token.text] = translated_text

    with open(translation_dict_path, "wb") as f:
        pickle.dump(translation_dict, f)


def translate_german_sentence_to_english(book_index, german_sentences):
    translated_texts = {book_index: []}
    matched_sentences_file_path = "matched_deepl_translations_multiple_books.pkl"
    if os.path.isfile(matched_sentences_file_path):
        with open(matched_sentences_file_path, "rb") as f:
            translated_texts = pickle.load(f)
        translated_texts[book_index] = []
    for sentence in german_sentences:
        translated = translate_wtih_deepl(sentence)
        if translated is None:
            continue
        translated_texts[book_index].append({
            "german_sentence": sentence,
            "english_machine_translation": translated
        })
    with open(matched_sentences_file_path, "wb") as f:
        pickle.dump(translated_texts, f)
    return translated_texts

def generate_token_information(book_index, german_sentences):
    tokenized_sentences_german = {book_index: []}
    token_dict_filename = "german_token_dicts.pkl"
    if os.path.isfile(token_dict_filename):
        with open(token_dict_filename, "rb") as f:
            tokenized_sentences_german = pickle.load(f)
        tokenized_sentences_german[book_index] = []
    for german_sentence in german_sentences:
        transformation = nlp(german_sentence)
        token_dicts = []
        for token in transformation:
            token_dict = {
                "word": str(token),
                "lemma":  str(token.lemma_),
                "function": spacy.explain(token.pos_)
            }
            token_dicts.append(token_dict)
        tokenized_sentences_german[book_index].append(token_dicts)
    with open(token_dict_filename, "wb") as f:
        pickle.dump(tokenized_sentences_german, f)

def translate_with_dictionary_update(book_index, german_text_filename):
    german_sentences = process_file(german_text_filename)
    #translate_german_sentence_to_english(book_index, german_sentences)
    generate_token_information(book_index, german_sentences)
    #update_deepl_translation_dict_from_file(german_sentences)

translate_with_dictionary_update(0, "Metamorphosis German.txt")
translate_with_dictionary_update(1, "Hänsel und Gretel.txt")
translate_with_dictionary_update(2, "Schneewittchen.txt")