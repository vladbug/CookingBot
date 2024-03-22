import pprint as pp
import OpenSearch.transformer as tr
import OpenSearch.opensearch as OpenSearchUtil
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from sklearn.feature_extraction.text import CountVectorizer

def embed_recipes(recipes, embedding_text):
    recipe_emb = tr.encode(embedding_text)
    for i,recipe in enumerate(recipes):
        recipe["sentence_embedding"] = recipe_emb[i].numpy()
        res = OpenSearchUtil.opensearch_end.add_recipe(i, recipe)
        pp.pprint(res)
        pp.pprint(recipe)
       


def populate_index(data):
    recipes = []
    embedding_text = []
    index = 0
    while True:
        try:
            document_sample = {}
            recipe_id = str(index)
            document_sample["recipeName"] = data[recipe_id]["displayName"]
            document_sample["prepTimeMinutes"] = data[recipe_id]["prepTimeMinutes"]
            document_sample["cookTimeMinutes"] = data[recipe_id]["cookTimeMinutes"]
            document_sample["totalTimeMinutes"] = data[recipe_id]["totalTimeMinutes"]
            document_sample["difficultyLevel"] = data[recipe_id]["difficultyLevel"]
            document_sample["images"] = [image["url"] for image in data[recipe_id]["images"]]
            document_sample["videos"] =[{ "title": video["title"], "url": video["url"]} for video in data[recipe_id]["videos"]] #Returns array of video objects
            document_sample["tools"] = [tool["displayName"] for tool in data[recipe_id]["tools"]]
            document_sample["cuisines"] = data[recipe_id]["cuisines"]
            document_sample["courses"] = data[recipe_id]["courses"]
            document_sample["diets"] = data[recipe_id]["diets"]
            document_sample["ingredients"] = [ing["displayText"] for ing in data[recipe_id]["ingredients"]]
            recipes.append(document_sample)

            vectorizer = CountVectorizer(ngram_range=(1,1),analyzer="word", stop_words='english')
            recipe_embeding_text = [document_sample["recipeName"] + " " + " ".join(document_sample["ingredients"])]
            vectorizer.fit_transform(recipe_embeding_text)
            recipe_embeding_text = " ".join(vectorizer.get_feature_names_out())
       
            embedding_text.append(recipe_embeding_text)

            index += 1
        except KeyError:
            print("End of data")
            embed_recipes(recipes, embedding_text)
            pp.pprint(document_sample)
            break
            

# document_sample = {
#     "recipeName": '',
#     "prepTimeMinutes": 0,
#     "cookTimeMinutes": 0,
#     "totalTimeMinutes": 0,
#     "difficultyLevel": '',
#     "images": '',
#     "videos": '', #complex object with title and url
#     "tools": '',
#     "cuisines": '',
#     "courses": '',
#     "diets": '',
#     "ingredients": '',
#     "sentence_embeddings": '', #Array that embeds the word
# }


#  "properties":{
#      "cuisines" : { #Array of cuisine types, "mexican", "Asian" etc..., [str]
#      "type" : "text" 
#      },
#      "courses" : { #Array of course types, "main" "breakfast" "sides" etc..., [str]
#          "type" : "text"
#      },
#      "diets" : { #Array of diet types, "vegan" etc... [str]
#          "type" : "text"
#      },
#      "ingredients" : { #Array of ingredient names, didn't save quantity cos that can be loaded later, [str]
#          "type" : "text", 
#      },