from flask import Flask
app = Flask(__name__)
#load up the semantic similarity
from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

@app.route("/")
def hello():
  return "Server Running!"

#get the sentences from the dataframe?
#or should we just go one at a time?
#maybe we just pass a row id and get the triples
#make sure it's rate limited so as not to kill the server
@app.route("/sentences")
def get_sentence():
    data = request.get_json()
    hwChannels = data["hwChannels"]  
    notes = []
    
    for hwChannel in hwChannels:
        sensorNotes = getNotesForSensor(hwChannel)
        notes.extend(sensorNotes)
    
    return jsonify(notes)

@app.route("/similarity")
def get_sentence():
    sentence1 = ""
    sentence2 = ""
    #Compute embedding for both lists
    embedding_1= model.encode(sentence1, convert_to_tensor=True)
    embedding_2 = model.encode(sentence2, convert_to_tensor=True)

    similarity = util.pytorch_cos_sim(embedding_1, embedding_2)
    return similarity

if __name__ == "__main__":
  app.run()