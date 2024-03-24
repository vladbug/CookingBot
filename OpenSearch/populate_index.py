import pprint as pp
import OpenSearch.transformer as tr
import OpenSearch.opensearch as OpenSearchUtil
from sklearn.feature_extraction.text import CountVectorizer
import os
import pickle

def embed_recipes(recipes, embedding_text):
    recipe_emb_file = 'recipe_emb.pkl'
    
    # Check if recipe_emb_file exists
    if os.path.exists(recipe_emb_file):
        # If file exists, load recipe_emb from the file
        with open(recipe_emb_file, 'rb') as f:
            recipe_emb = pickle.load(f)
    else:
        # If file does not exist, compute recipe_emb and save it to the file
        recipe_emb = tr.encode(embedding_text)
        with open(recipe_emb_file, 'wb') as f:
            pickle.dump(recipe_emb, f)

    for i,recipe in enumerate(recipes):
        recipe["sentence_embedding"] = recipe_emb[i].numpy()
        res = OpenSearchUtil.opensearch_end.add_recipe(i, recipe)
        pp.pprint(res)
       
def vectorize(text):
    vectorizer = CountVectorizer(ngram_range=(1,1),analyzer="word", stop_words='english')
    vectorizer.fit_transform(text)
    text = " ".join(vectorizer.get_feature_names_out())
    return text

def populate_index(data):
    recipes = []
    embedding_text = []

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
            recipe_sample["ingredients"] = [ing["displayText"] for ing in data[recipe_id]["ingredients"]]
            recipes.append(recipe_sample)

            recipe_text = [recipe_sample["recipeName"] + " " + " ".join(recipe_sample["ingredients"])]
            recipe_text = vectorize(recipe_text)
            embedding_text.append(recipe_text)
   
    embed_recipes(recipes, embedding_text)
