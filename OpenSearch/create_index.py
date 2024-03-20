import pprint as pp
from opensearchpy import OpenSearch
from opensearchpy import helpers

def create_index():
    env_file = open("OpenSearch/env_config.txt",'r')
    host_name = env_file.readline().split("=")[1]
    port = env_file.readline().split("=")[1]
    user_name = env_file.readline().split("=")[1]
    pwd = env_file.readline().split("=")[1]
    index_name = env_file.readline().split("=")[1]
    
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
        "dynamic":      "strict",
        "properties":{
            "displayName":{
                "type":"keyword"
            },
            "description":{
                "type":"keyword"
            },
            "canonicalName":{
                "type":"keyword"
            },
            "prepTimeMinutes":{
                "type":"keyword"
            },
            "cookTimeMinutes":{
                "type":"keyword"
            },
            "totalTimeMinutes":{
                "type":"keyword"
            },
            "cookingMethod":{
                "type":"keyword"
            },
            "difficultyLevel":{
                "type":"keyword"
            },
            "images":[{
                "url":"text",
                "hdUrl":"text",
                "fourKURL":"text",
                "type":"text"
            }],
            "videos": [{
                "providerId": "text",
                "title": "text",
                "url": "text",
                "mobileUrl": "text",
                "hdURL": "text",
                "fourKURL": "text",
                "description": "text",
                "type": "text"
            }],
            "tools" : [{
                "displayName":"text",
            }],
            
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


create_index()
