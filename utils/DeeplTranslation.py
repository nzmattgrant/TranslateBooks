import pandas
import requests
import pickle
from Configuration import DEEPL_API_KEY

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

translated_texts = []

for sentence in file1_sentences:
  tokens = nlp(sentence)
  for token in tokens:
    if token.is_punct or token.text in dict:
      #print("word already in dict or is puctuation", token.text)
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

with open("/content/drive/MyDrive/traslation_dict.pkl", "wb") as f:
    pickle.dump(dict, f)