from sentence_transformers import SentenceTransformer, util
import spacy
from flask import Flask, jsonify, request
import pandas as pd
from flask_cors import CORS
from PyMultiDictionary import MultiDictionary, DICT_EDUCALINGO
from nltk.stem.snowball import GermanStemmer
st = GermanStemmer()
nlp = spacy.load('de_dep_news_trf')
dictionary = MultiDictionary()
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
# load up the semantic similarity
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
file_name = 'matched_deepl_translations.pkl'
df = pd.read_pickle(file_name)


@app.route("/")
def hello():
  return "Server Running!"


@app.route("/sentences", methods=['GET'])
def get_sentence():
    args = request.args
    line_num = int(args['lineNumber'])
    print(line_num)
    print(df.shape)
    print(df)
    row = df.iloc[:, line_num]
    print(row)
    return [row.iloc[0], row.iloc[1]]


@app.route("/sentences2", methods=['GET'])
def get_sentence2():
    args = request.args
    line_num = int(args['lineNumber'])
    print(line_num)
    print(df.shape)
    print(df)
    row = df.iloc[:, line_num]
    print(row)
    presentation_sentence_tokens_with_definition = []
    presentation_sentence_tokenized = nlp(row.iloc[0])
    for token in presentation_sentence_tokenized:
      definition = dictionary.meaning(
          'de', token.lemma_, dictionary=DICT_EDUCALINGO)
      print(type(definition), len(definition), definition[2])
      presentation_sentence_tokens_with_definition.append({
          "word": str(token),
          "lemma":  str(token.lemma_),
          "definition": {
            "function": definition[0],
            "description": definition[1]
          }
      })
    second_sentence = row.iloc[1]

    return jsonify({
        "presentation_sentence_tokens": presentation_sentence_tokens_with_definition,
        "translation": second_sentence
    })


@app.route("/similarity", methods=['POST'])
def check_similarity():
    data = request.get_json()
    sentence1 = data["sentence1"]
    sentence2 = data["sentence2"]
    # Compute embedding for both lists
    embedding_1 = model.encode(sentence1, convert_to_tensor=True)
    embedding_2 = model.encode(sentence2, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(embedding_1, embedding_2)
    return {"similarity": similarity.item()}


@app.route("/translate", methods=['GET'])
def translate():
    args = request.args
    word = args['word']
    print(dictionary.meaning('de', word, dictionary=DICT_EDUCALINGO),
          dictionary.translate('de', word))
    return jsonify(dictionary.meaning('de', word, dictionary=DICT_EDUCALINGO))
    # return list(filter(lambda translation: translation[0] == "en", dictionary.translate('de', word)))[0][1]


@app.route("/stem", methods=['GET'])
def stem():
    args = request.args
    word = args['word']
    return jsonify(st.stem(word))


@app.route("/bookInfo", methods=['GET'])
def book_info():
   return {
       "bookTitle": "Thus spake Tharathustra",
       "numberOfSentences": df.shape[1]
   }


if __name__ == "__main__":
  app.run()
