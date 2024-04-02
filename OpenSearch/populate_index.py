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


embedding_files = ["Defs/sentence_embedding", "Defs/ingredient_embedding", "Defs/tools_embedding"]

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

def get_tools_text(recipe):
    tools = recipe["tools"]
    tools_text = ""
    if tools == []:
        return tools_text
    for tool in tools:
        tools_text += tool["displayName"] + " "
    return tools_text


        
def get_embedding_files():
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
    return embeddings, save_flags

def prepare_recipe_sample(data, index):
    recipe_sample = {}
    recipe_id = str(index)
    recipe_sample["recipeName"] = data[recipe_id]["displayName"]
    recipe_sample["prepTimeMinutes"] = data[recipe_id]["prepTimeMinutes"]
    recipe_sample["cookTimeMinutes"] = data[recipe_id]["cookTimeMinutes"]
    recipe_sample["totalTimeMinutes"] = data[recipe_id]["totalTimeMinutes"]
    recipe_sample["difficultyLevel"] = data[recipe_id]["difficultyLevel"]
    recipe_sample["images"] = [image["url"] for image in data[recipe_id]["images"]]
    recipe_sample["videos"] = [{ "title": video["title"], "url": video["url"]} for video in data[recipe_id]["videos"]]
    recipe_sample["tools"] = [tool["displayName"] for tool in data[recipe_id]["tools"]]
    recipe_sample["cuisines"] = data[recipe_id]["cuisines"]
    recipe_sample["courses"] = data[recipe_id]["courses"]
    recipe_sample["diets"] = data[recipe_id]["diets"]
    return recipe_sample

def process_embedding(embedding_text, embeddings, save_flags, embedding_files, recipe, index):
    recipe_sample = {}
    for file_name, embedding_text in zip(embedding_files, embedding_text):
        if save_flags[file_name]:
            embedding = tr.encode(embedding_text)
            embeddings[file_name].append(embedding)
        else:
            embedding = embeddings[file_name][index]
        index_field = file_name.split("/")[-1]
        if index_field == "ingredient_embedding":
            recipe_sample["ingredients"] = format_ingredients(embedding, recipe)
        else:
            recipe_sample[index_field] = embedding[0].numpy()
    return recipe_sample

def populate_index(data):
    embeddings, save_flags = get_embedding_files()

    for index in range(len(data)):
        recipe_sample = prepare_recipe_sample(data, index)
        recipe_id = str(index)
        #ingredients embedding text
        ing_text = ""
        if save_flags["Defs/ingredient_embedding"] or save_flags["Defs/sentence_embedding"]:
            ing_text = [ing["ingredient"] for ing in data[recipe_id]["ingredients"]]
        #title ingredients embedding text
        title_ing_text = ""
        if save_flags["Defs/sentence_embedding"]:
            title_ing_text = recipe_sample["recipeName"] + " " + " ".join(ing_text)
        #tools embedding text
        tools_text = ""
        if save_flags["Defs/tools_embedding"]:
            tools_text = get_tools_text(data[recipe_id])

        embeddings_text = [title_ing_text, ing_text, tools_text]
        
        recipe_sample = process_embedding(embeddings_text, embeddings, save_flags, embedding_files, data[recipe_id], index)

        res = OpenSearchUtil.opensearch_end.add_recipe(index, recipe_sample)
        pp.pprint(res)

     # update file embeddings if save flag is true
    for file_name, save in save_flags.items():
        if save:
            save_embedding_file(file_name, embeddings[file_name])
