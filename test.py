from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np
import nltk
nltk.download('averaged_perceptron_tagger')

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-mpnet-base-v2")

# Define two words
word1 = "gorgonzola"
word2 = "guacamole"

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


#___________________________________________________________________________________________________
from ingredient_parser import parse_ingredient

# Example usage
parsed_ingredient = parse_ingredient("1x cheese, 2x tomato")
print(parsed_ingredient)

#___________________________________________________________________________________________________
# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("token-classification", model="chambliss/distilbert-for-food-extraction")
# Load model directly
from transformers import AutoTokenizer, AutoModelForTokenClassification

tokenizer = AutoTokenizer.from_pretrained("chambliss/distilbert-for-food-extraction")
model = AutoModelForTokenClassification.from_pretrained("chambliss/distilbert-for-food-extraction")

# Example text
text = "I want a recipe with cheese and tomato."

# Tokenize input text
inputs = tokenizer(text, return_tensors="pt")

# Make predictions
outputs = model(**inputs)

# Decode the tokenized input to get the original words
decoded_tokens = tokenizer.decode(inputs['input_ids'][0])

# Split the decoded tokens to get individual words
original_words = decoded_tokens.split()

# Get the predicted class labels
predicted_class_indices = outputs.logits.argmax(-1)[0]

# Create a list to store words with label 0
parse_ingredient = []

# Iterate over the words and their predicted labels
for word, label in zip(original_words, predicted_class_indices):
    if label.item() == 0:  # Check if the label is 0
        parse_ingredient.append(word)

# Print the words with label 0
print(parse_ingredient)

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