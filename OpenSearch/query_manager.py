import pprint as pp
from typing import List, Union
import models.models as models
import OpenSearch.transformer as tr

class QueryManager():
    
    def __init__(self,client,index_name):
        self.client = client
        self.index_name = index_name
        

    
    #region Opensearch Text Queries
    def search_by_total_time(self, max_time: int, num_results=10):
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
        #endregion
    
    #region Opensearch Embedding Queries
    def text_query(self, query : str):
        query_emb = tr.encode(query)
        embedding = query_emb[0].numpy()
        query_denc = {
           'size': 10,
           "_source": ["recipeName","prepTimeMinutes","cookTimeMinutes","totalTimeMinutes","difficultyLevel","tools","ingredients.name"],
            "query": {
               "knn": {
                    "description_embedding": {
                        "vector": embedding,
                        "k": 3
                    }
                }
            }
        }
        response = self.client.search(index=self.index_name, body=query_denc)
        print('\nSearch Result:')
        pp.pprint(response)
    
    def query_by_ingredient(self, query : str):
        parsed_ingredients = models.get_ing_from_sentence(query)
    
        query_denc = {
                'size': 5,
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
                                "vector": tr.encode(ingredient)[0].numpy(),  # Assuming ingredient has an embedding attribute
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
    #endregion 
    
    

        

