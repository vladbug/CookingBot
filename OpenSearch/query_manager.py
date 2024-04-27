import pprint as pp
from typing import List, Union
import models.models as models
import OpenSearch.transformer as tr
from opensearchpy import OpenSearch
from models.Clip import CLIPClass
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
        parsed_ingredients = models.get_ing_from_sentence(query)
    
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
        query_emb = self.clip.get_text_embedding(query)
        embedding = query_emb[0].numpy()
        query_denc = {
           'size': num_results,
           "_source": ["recipeName","images","ingredients.name"],
                "query": {
                    "knn": {
                        "image_embedding": {
                            "vector":embedding, 
                            "k": 3
                        }
                    }
                }       
        }
        response = self.client.search(index=self.index_name, body=query_denc)
        print('\nSearch Result:')
        pp.pprint(response)
    #endregion 