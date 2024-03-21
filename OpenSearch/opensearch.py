from typing import Tuple
import OpenSearch.transformer as tr
from opensearchpy import OpenSearch
import pprint as pp


class OpenSearchEnd:
    def __init__(self):
        env_file = open("OpenSearch/env_config.txt",'r')
        self.host_name = env_file.readline().split("=")[1].strip()
        self._port = int(env_file.readline().split("=")[1].strip())
        self._user_name = env_file.readline().split("=")[1].strip()
        self._pwd = env_file.readline().split("=")[1].strip()
        self.index_name = self._user_name
        self.client = None
    
    def connect(self):
        self.client = OpenSearch(
            hosts = [{'host': self.host_name, 'port': self._port}],
            http_compress = True, # enables gzip compression for request bodies
            http_auth = (self._user_name, self._pwd),
            url_prefix = 'opensearch',
            # client_cert = client_cert_path,
            # client_key = client_key_path,
            use_ssl = True,
            verify_certs = False,
            ssl_assert_hostname = False,
            ssl_show_warn = False
            #, ca_certs = ca_certs_path
            )
        return self.client

    def disconnect(self):
        if self.client is None:
            return
        return self.client.indices.close(index = self.index_name, timeout=600)
    
    def create_index(self):
        index_body = {
            "settings":{
                "index":{
                    "number_of_replicas":0,
                    "number_of_shards":4,
                    "refresh_interval":"-1",
                    "knn":"true"
                }
            },    
            "mappings":{
                "dynamic":"strict",
                "properties":{
                    "recipeName":{ #name of the recipe
                        "type":"text"
                    },
                    "prepTimeMinutes":{ #Preparation time in minutes, always int
                        "type":"integer"
                    },
                    "cookTimeMinutes":{ #Cooking time in minutes, always int
                        "type":"integer"
                    },
                    "totalTimeMinutes":{ #Total cooking time in minutes, always int
                        "type":"integer"
                    },
                    "difficultyLevel":{ #Difficulty level of recipe (easy/medium/hard)
                        "type":"text"
                    },
                    "images":{ #Array of image urls, [str]
                        "type" : "text"  
                    },
                    "videos": { #Array of object type videos, that contains a title and url
                        "type": "nested",
                        "properties": {
                        "title": {
                            "type": "text"
                        },
                        "url": {
                            "type": "text"
                        }
                        }
                    },
                    "tools" : { #Array of tool names, [str]
                        "type":"text",
                    },
                    "cuisines" : { #Array of cuisine types, "mexican", "Asian" etc..., [str]
                    "type" : "text" 
                    },
                    "courses" : { #Array of course types, "main" "breakfast" "sides" etc..., [str]
                        "type" : "text"
                    },
                    "diets" : { #Array of diet types, "vegan" etc... [str]
                        "type" : "text"
                    },
                    "ingredients" : { #Array of ingredient names, didn't save quantity cos that can be loaded later, [str]
                        "type" : "text", 
                    },
                    "contents":{ 
                        "type":"text",
                        "analyzer": "standard",
                        #"analyzer":"my_analyzer", we can after add the spell checking here
                        "similarity":"BM25"
                    },
                    "sentence_embedding":{
                        "type":"knn_vector",
                        "dimension": 768,
                        "method":{
                        "name":"hnsw",
                        "space_type":"innerproduct",
                        "engine":"faiss",
                        "parameters":{
                            "ef_construction":256,
                            "m":48
                        }
                        }
                    }
                }
            }
        }
        
        if self.client.indices.exists(index=self.index_name):
            print("Index already existed. Nothing to be done.")
        else:        
            response = self.client.indices.create(self.index_name, body=index_body)
            print('\nCreating index:')
            if(response["acknowledged"] == True):
                print("Index created successfully!")


    
    def delete_index(self):
        #answer = input("ARE YOU ABSOLUTELY SURE YOU WANT TO DELETE THE INDEX?\nPlease type: \"I am sure of it\" if you are: ")
        if(True):
            if self.client.indices.exists(index=self.index_name):
                # Delete the index.
                response = self.client.indices.delete(
                    index = self.index_name,
                    timeout = 600
                )
                print("Deleted: {0}".format(response["acknowledged"]))

    def add_recipe(self, id: int, recipe : dict) -> dict:
        resp = self.client.index(index=self.index_name, id=id, body=recipe)
        return resp            
    
    def query(self):
        query = "tomato"
        query_emb = tr.encode(query)

        query_denc = {
            "size": 5,
            '_source': 'recipeName',
            "query": {
                "knn": {
                    "sentence_embedding": {
                        "vector": query_emb[0].numpy(),
                        "k": 2
                    }
                }
            }
        }
        response = self.client.search(index=self.index_name, body=query_denc)
        pp.pprint(self.client.cat.count(index=self.index_name))
        print('\nSearch Result:')
        pp.pprint(response)

opensearch_end = OpenSearchEnd() 