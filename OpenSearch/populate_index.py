import pprint as pp
import OpenSearch.transformer as tr
import OpenSearch.opensearch as OpenSearchUtil
from sklearn.feature_extraction.text import CountVectorizer
import os
import pickle
import nltk
nltk.download('averaged_perceptron_tagger')
from ingredient_parser import parse_ingredient
from deep_translator import GoogleTranslator

def read_embedding_file(file_name):
    # Check if recipe_emb_file exists
    if os.path.exists(file_name):
        # If file exists, load recipe_emb from the file
        with open(file_name, 'rb') as f:
            return pickle.load(f)
    else:
        return None
    
def save_embedding_file(file_name, recipe_emb):
    with open(file_name, 'wb') as f:
        pickle.dump(recipe_emb, f)    

# This function already receives the embedding of the ingredients
def format_ingredients(embedding,recipe):
    ing_obj = []
    for idx, ing in enumerate(recipe["ingredients"]):
        ing_obj.append({"name":ing["ingredient"], 
                        "ingredient_embedding":embedding[idx].numpy()})
    return ing_obj

# deprecated - done in test.py
def complete_ingredient(recipe):
    translator = GoogleTranslator(source='auto', target='en')
    for ing in recipe["ingredients"]:
        if ing["ingredient"] is None:
            myDisplayText = ing["displayText"]
            ingredient =  translator.translate(myDisplayText)
            ingredient = parse_ingredient(ingredient)["name"]
            ing["ingredient"] = ingredient

def populate_index(data):
    embedding_files = ["Defs/sentence_embedding", "Defs/ingredient_embedding"]
    embeddings = {}
    save_flags = {}
    for file_name in embedding_files:
        embedding_file = read_embedding_file(file_name)
        if embedding_file is None:
            embeddings[file_name] = []
            save_flags[file_name] = True
        else:
            embeddings[file_name] = embedding_file
            save_flags[file_name] = False
    pp.pprint(save_flags)

    for index in range(len(data)):
        recipe_sample = {}
        recipe_id = str(index)
        recipe_sample["recipeName"] = data[recipe_id]["displayName"]
        recipe_sample["prepTimeMinutes"] = data[recipe_id]["prepTimeMinutes"]
        recipe_sample["cookTimeMinutes"] = data[recipe_id]["cookTimeMinutes"]
        recipe_sample["totalTimeMinutes"] = data[recipe_id]["totalTimeMinutes"]
        recipe_sample["difficultyLevel"] = data[recipe_id]["difficultyLevel"]
        recipe_sample["images"] = [image["url"] for image in data[recipe_id]["images"]]
        recipe_sample["videos"] =[{ "title": video["title"], "url": video["url"]} for video in data[recipe_id]["videos"]]
        recipe_sample["tools"] = [tool["displayName"] for tool in data[recipe_id]["tools"]]
        recipe_sample["cuisines"] = data[recipe_id]["cuisines"]
        recipe_sample["courses"] = data[recipe_id]["courses"]
        recipe_sample["diets"] = data[recipe_id]["diets"]
       
        #complete ingredients
        #complete_ingredient(data[recipe_id])
        #title ingredients embeddings
        ing_text = [ing["ingredient"] for ing in data[recipe_id]["ingredients"]]
        title_ing_text = recipe_sample["recipeName"] + " " + " ".join(ing_text)

        embeddings_text = [title_ing_text, ing_text]

       
        for file_name, embedding_text in zip(embedding_files, embeddings_text):
            if save_flags[file_name]:
                embedding = tr.encode(embedding_text)
                embeddings[file_name].append(embedding)
            else:
                embedding = embeddings[file_name][index]
            index_field = file_name.split("/")[-1]
            if index_field == "ingredient_embedding":
               recipe_sample["ingredients"] = format_ingredients(embedding, data[recipe_id])
            else:
                recipe_sample[index_field] = embedding[0].numpy()

        res = OpenSearchUtil.opensearch_end.add_recipe(index, recipe_sample)
        pp.pprint(res)

     # update file embeddings if save flag is true
    for file_name, save in save_flags.items():
        if save:
            save_embedding_file(file_name, embeddings[file_name])

