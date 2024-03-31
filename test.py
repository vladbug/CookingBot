from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import nltk
nltk.download('averaged_perceptron_tagger')

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-mpnet-base-v2")

# Define two words
word1 = "kitchen"
word2 = "boy"

# Tokenize and encode the words
inputs = tokenizer([word1, word2], return_tensors="pt", padding=True, truncation=True)
with torch.no_grad():
    outputs = model(**inputs)

# Extract embeddings
embeddings = outputs.last_hidden_state

def cos_sim(x, y):
    # Compute cosine similarity
    similarity = np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y))
    return similarity

# Extract vectors for each word
embedding_word1 = embeddings[0].mean(dim=0).cpu().numpy()  # Average pooling over tokens
embedding_word2 = embeddings[1].mean(dim=0).cpu().numpy()

# Compute cosine similarity
cosine_similarity = cos_sim(embedding_word1, embedding_word2)
print("Cosine similarity Score: {:.4f}".format(cosine_similarity))



from ingredient_parser import parse_ingredient

# Example usage
parsed_ingredient = parse_ingredient("2 yellow onions, finely chopped")
print(parsed_ingredient)

#___________________________________________________________________________________________________
import json
from deep_translator import GoogleTranslator

def load_json():
    with open("./Defs/recipes_data.json", "r") as read_file:
        data = json.load(read_file)
    return data

def complete_ingredient(recipe):
    translator = GoogleTranslator(source='auto', target='en')
    for ing in recipe["ingredients"]:
        if ing["ingredient"] is None:
            myDisplayText = ing["displayText"]
            ingredient =  translator.translate(myDisplayText)
            ingredient = parse_ingredient(ingredient)["name"]
            ing["ingredient"] = ingredient

def save_json():
    data = load_json()
    for index in range(len(data)):
        recipe_id = str(index)
        complete_ingredient(data[recipe_id])
    with open("./Defs/recipes_data_comp_trans.json", "w") as write_file:
        json.dump(data, write_file, indent=4)
#save_json()