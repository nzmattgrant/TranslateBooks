from flask import Flask, request
import pandas as pd
from flask_cors import CORS, cross_origin
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
#load up the semantic similarity
from sentence_transformers import SentenceTransformer, util
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



@app.route("/similarity", methods=['POST'])
def check_similarity():
    data = request.get_json()
    sentence1 = data["sentence1"]
    sentence2 = data["sentence2"]
    #Compute embedding for both lists
    embedding_1= model.encode(sentence1, convert_to_tensor=True)
    embedding_2 = model.encode(sentence2, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(embedding_1, embedding_2)
    return {"similarity": similarity.item()}

@app.route("/bookInfo", methods=['GET'])
def book_info():
   return {
      "bookTitle": "Thus spake Tharathustra",
      "numberOfSentences": df.shape[1]
   }

if __name__ == "__main__":
  app.run()