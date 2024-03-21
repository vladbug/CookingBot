from typing import Tuple
from opensearchpy import OpenSearch

def create_index() -> Tuple[OpenSearch,str] :
    env_file = open("OpenSearch/env_config.txt",'r')
    host_name = env_file.readline().split("=")[1].strip()
    port = int(env_file.readline().split("=")[1].strip())
    user_name = env_file.readline().split("=")[1].strip()
    pwd = env_file.readline().split("=")[1].strip()
    index_name = user_name

    
    # Create the client with SSL/TLS enabled, but hostname verification disabled.
    client = OpenSearch(
    hosts = [{'host': host_name, 'port': port}],
    http_compress = True, # enables gzip compression for request bodies
    http_auth = (user_name, pwd),
    url_prefix = 'opensearch',
    # client_cert = client_cert_path,
    # client_key = client_key_path,
    use_ssl = True,
    verify_certs = False,
    ssl_assert_hostname = False,
    ssl_show_warn = False
    #, ca_certs = ca_certs_path
)
    
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
                    #"analyzer":"my_analyzer",
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
    
    if client.indices.exists(index=index_name):
        #print("Index already existed. Nothing to be done.")
        return (client,index_name)
    else:        
        response = client.indices.create(index_name, body=index_body)
        print('\nCreating index:')
        if(response["acknowledged"] == True):
            print("Index created successfully!")
            return (client, index_name)

def delete_index(client : OpenSearch,index_name : str) -> None:
    answer = input("ARE YOU ABSOLUTELY SURE YOU WANT TO DELETE THE INDEX?\nPlease type: \"I am sure of it\" if you are: ")
    if(answer == "I am sure of it"):
        if client.indices.exists(index=index_name):
            # Delete the index.
            response = client.indices.delete(
                index = index_name,
                timeout = 600
            )
            print("Deleted: {0}".format(response["acknowledged"]))
    
   
create_index()
