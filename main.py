import json
import OpenSearch.opensearch as OpenSearchUtil 
import OpenSearch.populate_index as populateIndex
import OpenSearch.textQueries as t_queries

def load_json():
    with open("./Defs/recipes_data_comp_trans.json", "r") as read_file:
        data = json.load(read_file)
    return data

data = load_json()
OpenSearchUtil.opensearch_end.disconnect()
client_info = OpenSearchUtil.opensearch_end.connect()
client = client_info[0]
index_name = client_info[1]
# TODO NAO CORRER ESTAS TRES LINHAS
# OpenSearchUtil.opensearch_end.delete_index()
# OpenSearchUtil.opensearch_end.create_index()
#populateIndex.populate_index(data=data)

t_queries.search_ingredients_bool(client,index_name,"")