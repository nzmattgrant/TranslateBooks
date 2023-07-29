from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
import nltk
nltk.download('punkt')
from nltk.tokenize import sent_tokenize, word_tokenize
import pickle

def process_file(file_name):
    with open(file_name, "r", encoding='utf-8-sig') as file:
        text = file.read()
        lines = text.strip().split("\n")
        lines = [line.strip() for line in lines if line.strip()]
        text = " ".join(lines)
        sentences = sent_tokenize(text)
        return sentences

file1_sentences = process_file("Metamorphosis German.txt")
file2_sentences = process_file("Metamorphosis English.txt")


with open("../server/matched_deepl_translations_multiple_books.pkl", "rb") as f:
    matched_translations = pickle.load(f)[0]
    print(matched_translations)

matched_translations = list(matched_translations.values())

def calculate_similarity(original_sentence, sentences_to_compare):
  original_sentence_embedding = model.encode(original_sentence, convert_to_tensor=True)
  sentences_to_compare_embeddings = [model.encode(sentence, convert_to_tensor=True) for sentence in sentences_to_compare]
  similarities = [util.pytorch_cos_sim(original_sentence_embedding, sentence).item() for sentence in sentences_to_compare_embeddings]
  return similarities

best_matches = []
machine_translation_index = 0
human_translation_index = 0
while machine_translation_index < len(matched_translations) and human_translation_index < len(file2_sentences):
  similarities = []
  german_sentence = matched_translations[machine_translation_index]["german_sentence"]
  english_machine_translation = matched_translations[machine_translation_index]["english_machine_translation"]
  english_human_translation = file2_sentences[human_translation_index]
  next_human_index = human_translation_index + 1
  next_human_to_test = []
  while next_human_index < human_translation_index+3 and next_human_index < len(file2_sentences):
    next_human_to_test.append(file2_sentences[next_human_index])
    next_human_index += 1
  next_machine_index = machine_translation_index + 1
  next_machine_to_test = []
  while next_machine_index < machine_translation_index+3 and next_machine_index < len(matched_translations):
    next_machine_to_test.append(matched_translations[next_machine_index])
    next_machine_index += 1
  next_scores = []
  next_scores_index = 0
  while next_scores_index < len(next_human_to_test) and next_scores_index < len(next_machine_to_test):
    next_scores = next_scores + calculate_similarity(next_human_to_test[next_scores_index], next_machine_to_test[next_scores_index])
    next_scores_index += 1
    
  current_match = calculate_similarity(file2_sentences[human_translation_index], matched_translations[machine_translation_index])[0]
  print("next scores", next_scores)
  next_matches_are_better = len(next_scores) > 0 and all([score > current_match for score in next_scores])
  if not next_matches_are_better:
    human_sentences_to_test = []
    for i in range(1, min(len(file2_sentences) - human_translation_index, 3)+1):
      human_sentences_to_test.append(" ".join(file2_sentences[human_translation_index:human_translation_index+i]))
    machine_to_multiple_human_similarity = calculate_similarity(english_machine_translation, human_sentences_to_test)
    print("test", machine_to_multiple_human_similarity)
    best_machine_to_multiple_human_similarity = max(machine_to_multiple_human_similarity)
    best_machine_to_multiple_human_similarity_index = machine_to_multiple_human_similarity.index(best_machine_to_multiple_human_similarity)

    machine_sentences_to_test = []
    for i in range(1, min(len(matched_translations) - machine_translation_index, 3)+1):
      slicey = list(matched_translations[machine_translation_index:machine_translation_index+i])
      matched_sentences_to_join = map(lambda x: x["english_machine_translation"], slicey)
      machine_sentences_to_test.append(" ".join(matched_sentences_to_join))
    human_to_multiple_machine_similarity = calculate_similarity(english_human_translation, machine_sentences_to_test)
    print("test", human_to_multiple_machine_similarity)
    best_human_to_multiple_machine_similarity = max(human_to_multiple_machine_similarity)
    best_human_to_multiple_machine_similarity_index = human_to_multiple_machine_similarity.index(best_human_to_multiple_machine_similarity)
    print(best_machine_to_multiple_human_similarity_index, best_human_to_multiple_machine_similarity_index)

    if best_machine_to_multiple_human_similarity_index != 0 or best_human_to_multiple_machine_similarity_index != 0:
      if best_machine_to_multiple_human_similarity > best_human_to_multiple_machine_similarity:
        to_add = best_machine_to_multiple_human_similarity_index
        english_human_translation = " ".join(file2_sentences[human_translation_index:human_translation_index+to_add+1])
        human_translation_index += to_add
      else:
        to_add = best_human_to_multiple_machine_similarity_index
        matched_translations_slice = matched_translations[machine_translation_index:machine_translation_index+to_add+1]
        german_sentence = " ".join(map(lambda x: x["german_sentence"], matched_translations_slice))
        english_machine_translation = " ".join(map(lambda x: x["english_machine_translation"], matched_translations_slice))
        machine_translation_index += to_add

  new_best_match = {
    "german_sentence": german_sentence,
    "english_machine_translation": english_machine_translation,
    "english_human_translation": english_human_translation
  }
  print(new_best_match)
  best_matches.append(new_best_match)
  machine_translation_index += 1
  human_translation_index += 1
with open("matched_deepl_translation_triplets_multiple_books.pkl", "wb") as f:
    pickle.dump({0: best_matches}, f)