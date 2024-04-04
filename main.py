import json
import OpenSearch.opensearch as OpenSearchUtil 
import OpenSearch.populate_index as populateIndex
import OpenSearch.query_manager as query_manager
import time 
import pprint as pp

def load_json():
    with open("./Defs/recipes_data_comp_trans.json", "r") as read_file:
        data = json.load(read_file)
    return data

data = load_json()
OpenSearchUtil.opensearch_end.disconnect()
client_info = OpenSearchUtil.opensearch_end.connect()
client = client_info[0]
index_name = client_info[1]
query_manager = query_manager.QueryManager(client,index_name)
# TODO NAO CORRER ESTAS TRES LINHAS
#OpenSearchUtil.opensearch_end.delete_index()
#OpenSearchUtil.opensearch_end.create_index()
#populateIndex.populate_index(data=data)

query_manager = query_manager.QueryManager(client,index_name)
query_manager.search_by_difficulty("easy",10)
