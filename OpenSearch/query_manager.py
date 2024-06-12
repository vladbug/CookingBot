import pprint as pp
from typing import List
import models.models as ing_extractor
from models.Clip import CLIPClass
import OpenSearch.transformer as tr
from opensearchpy import OpenSearch
import math
import pprint as pp

"""
Class responsible for querying our recipes
"""

class QueryManager():
    
    def __init__(self,client : OpenSearch,index_name : str):
        self.client = client
        self.index_name = index_name
        self.clip = CLIPClass()
        
    #region Opensearch Text Queries - Simple text queries
    
    #Total time it takes to compute the recipe
    def search_by_total_time(self, max_time: int, num_results=1):
        total_time_query = {
            'size': num_results,
            "_source": ["recipeName", "totalTimeMinutes", "difficultyLevel"],
            'query': {
                'range': {
                    'totalTimeMinutes': {'lte': max_time}
                }
            }
        }

        response = self.client.search(
            body=total_time_query,
            index=self.index_name
        )

        print('\nSearch results:')
        pp.pprint(response)

    
    #Search by a given difficulty, easy, medium, hard
    def search_by_difficulty(self, difficulty_query : str, num_results = 1):
        query_body = {
            'size': num_results,
            "_source": ["recipeName","totalTimeMinutes","difficultyLevel"],
            'query' : {
                'multi_match' : {
                    'query': difficulty_query,
                    'fields': ['difficultyLevel']
                }
            }
        }
        
        pp.pprint(query_body)
        response = self.client.search(
            body=query_body,
            index=self.index_name,
            timeout=50
        )
        
        print('\nSearch results:')
        pp.pprint(response)

    #Search by a given course, main, dessert, breakfast etc...
    def search_by_course(self, query : str, num_results = 1):
        
        difficulty_query = {
            'size': num_results,
            "_source": ["recipeName","totalTimeMinutes","courses"],
            'query' : {
                'multi_match' : {
                    'query': query,
                    'fields': ['courses']
                }
            }
        }
        
        response = self.client.search(
            index=self.index_name,
            body=difficulty_query
        )
        
        print('\nSearch results:')
        pp.pprint(response)
    
    
    def search_ingredients_bool(self, ingredients_included : List[str], ingredients_excluded : List[str], num_results = 5):
        
        query_body = {
                'size': num_results,
                "_source": ["recipeName","totalTimeMinutes","ingredients.name"],
                "query": {
                    "bool": {
                        "must": [],
                        "must_not": []
                    }
                }
            }
        for ingredient in ingredients_included:
            query_body["query"]["bool"]["must"].append({
                "nested": {
                    "path": "ingredients",
                    "query": {
                        "match": {
                            "ingredients.name": ingredient
                        }
                    }
                }
            })
        for ingredient in ingredients_excluded:
            query_body["query"]["bool"]["must_not"].append({
                "nested": {
                    "path": "ingredients",
                    "query": {
                        "match": {
                            "ingredients.name": ingredient
                        }
                    }
                }
            })

    
        response = self.client.search(
            body=query_body,
            index=self.index_name,            
        )
    
        print('\nSearch results:')
        pp.pprint(response)
    
    
    #Search by a given number of servings, can be exact or up to the given number
    def search_by_servings(self, nr_servings, exact = True, num_results = 1):
        
        if(exact):
            query_body = {
                'size' : num_results,
                '_source' : ["recipeName","servings","ingredients.name"],
                'query': {
                    'multi_match' : {
                        'query' : nr_servings,
                        'fields' : ["servings"]
                    }
                }
            }
        else:
            query_body = {
            'size': num_results,
            "_source": ["recipeName", "totalTimeMinutes", "difficultyLevel"],
            'query': {
                'range': {
                    'fields': {'gte': nr_servings}
                }
            }
        }
            
        response = self.client.search(
            body=query_body,
            index=self.index_name,            
        )
    
        print('\nSearch results:')
        pp.pprint(response)
    #endregion
    
    #region Opensearch Embedding Queries
        
    def text_query(self, query : str, num_results = 1):
        query_emb = tr.encode(query)
        embedding = query_emb[0].numpy()
        query_denc = {
           'size': num_results,
           "_source": ["ingredients.name", "recipeName", "tools"],
            "query": {
               "nested": {
                    "path": "steps_embedding",
                    "query": {
                        "knn": {
                            "steps_embedding.step_embedding": {
                                "vector":embedding, 
                                "k": 3
                            }
                        }
                    }
                }
            }
        }
        response = self.client.search(index=self.index_name, body=query_denc)
        print('\nSearch Result:')
        pp.pprint(response)
    
    def query_by_ingredient(self, query : str, num_results = 1):
        parsed_ingredients = ing_extractor.get_ing_from_sentence(query)
    
        query_denc = {
                'size': num_results,
                "_source": ["recipeName", "prepTimeMinutes", "cookTimeMinutes", "totalTimeMinutes", "difficultyLevel",
                            "tools", "ingredients.name"],
                "query": {
                    "bool": {
                        "must": []
                    }
                }
            }

            # Iterate over each parsed ingredient and add a KNN field for it
        for ingredient in parsed_ingredients:
            # Create a new KNN field for the ingredient
            print(ingredient)
            knn_field = {
                "nested": {
                    "path": "ingredients",
                    "query": {
                        "knn": {
                            "ingredients.ingredient_embedding": {
                                "vector": tr.encode(ingredient)[0].numpy(),
                                "k": 3
                            }
                        }
                    }
                }
            }
            # Add the KNN field to the "must" list in the query
            query_denc["query"]["bool"]["must"].append(knn_field)

        # Perform the Elasticsearch search
        response = self.client.search(index=self.index_name, body=query_denc)
        print('\nSearch Result:')
        pp.pprint(response)

    
            
    def query_by_img(self, query : str, num_results = 1):
        
        query_emb = self.clip.get_image_embedding(query)
        embedding = query_emb[0].numpy()
        query_body = {
        'size': num_results/2 + (math.ceil(num_results % 2)),
        '_source': ['recipeName', 'images', 'ingredients.name'],
        'query': {
            'nested': {
                'path': 'image_embedding',
                'query': {
                    'knn': {
                        'image_embedding.text_embedding': {
                            'vector': embedding,
                            'k': 3
                        }
                    }
                },
            }
        },
    }
        txt_response = self.client.search(index=self.index_name, body=query_body)
        
        query_body = {
        'size': num_results/2,
        '_source': ['recipeName', 'images', 'ingredients.name'],
        'query': {
            'nested': {
                'path': 'image_embedding',
                'query': {
                    'knn': {
                        'image_embedding.img_embedding': {
                            'vector': embedding,
                            'k': 3
                        }
                    }
                },
            }
        },
    }
        img_response = self.client.search(index=self.index_name, body=query_body)
        response = txt_response['hits']['hits'] + img_response['hits']['hits']

        unique_recipes = set()
        unique_response = []
        for hit in response:
            recipe_id = hit['_id']  # Assuming recipe ID is stored in '_id'
            if recipe_id not in unique_recipes:
                unique_recipes.add(recipe_id)
                unique_response.append(hit)
        print('\nSearch Result:')
        pp.pprint(response)

    def query_by_txt(self, query : str, num_results = 1):
        query_emb = self.clip.get_text_embedding(query)
        embedding = query_emb[0].numpy()
        query_body = {
        'size': num_results/2 + (math.ceil(num_results % 2)),
        '_source': ['recipeName', 'images', 'ingredients.name'],
        'query': {
            'nested': {
                'path': 'image_embedding',
                'query': {
                    'knn': {
                        'image_embedding.text_embedding': {
                            'vector': embedding,
                            'k': 3
                        }
                    }
                },
            }
        },
        }   
        txt_response = self.client.search(index=self.index_name, body=query_body)
        
        query_body = {
        'size': num_results/2,
        '_source': ['recipeName', 'images', 'ingredients.name'],
        'query': {
            'nested': {
                'path': 'image_embedding',
                'query': {
                    'knn': {
                        'image_embedding.img_embedding': {
                            'vector': embedding,
                            'k': 3
                        }
                    }
                },
            }
        },
    }
        img_response = self.client.search(index=self.index_name, body=query_body)
        response = txt_response['hits']['hits'] + img_response['hits']['hits']

        unique_recipes = set()
        unique_response = []
        for hit in response:
            recipe_id = hit['_id']  # Assuming recipe ID is stored in '_id'
            if recipe_id not in unique_recipes:
                unique_recipes.add(recipe_id)
                unique_response.append(hit)
        print('\nSearch Result:')
        pp.pprint(response)
        
    #endregion 
    
    #region - Generic OpenSearch query, with slotfilling variables
    
    def query_generic_opensearch(self, slot_variables : dict[str:str],num_results = 1, suggestion = False):
        
        """
        Slot variables is a dictionary with variables that were filled by the SlotFilling class
        
        For really generic suggestions we have:
        generic - Generic information of what the user wants
        occasion - Information about the occasion, like a birthday party
        ingredients - The ingredients we want included
        
        For other type of suggestions ("I want to make X with Y ingredients etc...") we have:
        generic - Generic information about the recipe they want to make
        ingredients - the ingredients
        duration - the duration
        servings - the servings
        style - the style of cooking, such as mediterranean
        difficulty - the difficulty of the recipe
        """
        
        #Segments to fill in the query
        query_sources = []
        
        if(suggestion):
            query_sources = ["recipe_json", "recipeName",'ingredients.name','difficultyLevel','totalTimeMinutes']
            num_results = max(num_results,5) #Minimum top 5 suggestions
        else:#Search
            query_sources = ["recipe_json", "recipeName", 'ingredients.name', 'difficultyLevel', 'totalTimeMinutes']
            num_results = max(num_results,3) #Minimum top 3 
 
        template_query = {
            'size': num_results,
            '_source' : query_sources,
            'query' : {
                "bool": {
                        "must": [],
                        "should" : []
                }
            }
        }
        
        #region - Add generic info to the query
        generic_info_embedding = tr.encode(slot_variables['generic'])
        
        #Compute embedding for the generic info
        generic_embedding = generic_info_embedding[0].numpy()
        
        #Call function to fill in the slots on the template embedding
        embedding_query_element = set_embedding_info('steps_embedding.step_embedding',generic_embedding,'steps_embedding')
        
        template_query['query']['bool']['must'].append(embedding_query_element)
        #endregion
        
        #region Add ingredient information to the query, TODO: extract only the exact ingredients
        
        ingredient_info_embedding = tr.encode(slot_variables['ingredients'])
        ingredient_embedding = ingredient_info_embedding[0].numpy()
        embedding_query_element = set_embedding_info('ingredients.ingredient_embedding', ingredient_embedding, 'ingredients')
        template_query['query']['bool']['must'].append(embedding_query_element) 
        #endregion
        
        #region - Add optional slot filling variables
        if(slot_variables['ingredients'] != "NULL"):
            template_query = add_ingredients_to_query(template_query, slot_variables['ingredients'])
        
        if(not suggestion):
            if(slot_variables['duration'] != "NULL"):template_query['query']['bool']['should'].append(set_should_info('totalTimeMinutes',slot_variables['duration']))
            if(slot_variables['servings'] != "NULL"):template_query['query']['bool']['should'].append(set_should_info('servings',slot_variables['servings']))
            if(slot_variables['style'] != "NULL"):template_query['query']['bool']['should'].append(set_should_info('cuisines',slot_variables['style']))
            if(slot_variables['difficulty'] != "NULL"):template_query['query']['bool']['should'].append(set_should_info('difficultyLevel',slot_variables['difficulty']))
        
        #pp.pprint("\n\nFinal Query shape:\n{0}\n\n".format(template_query['query']['bool']['should']))
        
        response = self.client.search(index=self.index_name, body=template_query)
        return response
        #print('\nSearch Result:')
        #pp.pprint(response)
        
    #endregion
    
#region - Auxiliary functions for generic template query
def set_embedding_info(embedding_category, embedding, path):
    embedding_template = {
        "nested": {
            "path": path,
            "query": {
                "knn": {
                    embedding_category: {
                        "vector":embedding, 
                        "k": 3
                    }
                }
            }
        }
    }
    return embedding_template

def set_should_info(name, variable):
    embedding_template = {
                "match": {
                    name: variable
                }
            }
    return embedding_template
    
def add_ingredients_to_query(template_query, ingredients):
    
    ingredients_list = ing_extractor.get_ing_from_sentence(ingredients)
    for ing in ingredients_list:
        embedding_template = {
            "nested": {
                "path": 'ingredients',
                "query": {
                    "match": {
                        'ingredients.name': ing
                    }
                }
            }
        }
        template_query['query']['bool']['should'].append(embedding_template) 
    #print("Ingredients added to should clause: {0}".format(template_query['query']['bool']['should']))
    return template_query
#endregion