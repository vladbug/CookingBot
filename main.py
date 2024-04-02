import json
import OpenSearch.opensearch as OpenSearchUtil 
import OpenSearch.populate_index as populateIndex
import time 
import OpenSearch.textQueries as queries

def load_json():
    with open("./Defs/recipes_data_comp_trans.json", "r") as read_file:
        data = json.load(read_file)
    return data

data = load_json()
OpenSearchUtil.opensearch_end.disconnect()
OpenSearchUtil.opensearch_end.connect()
# TODO NAO CORRER ESTAS TRES LINHAS
# OpenSearchUtil.opensearch_end.delete_index()
# OpenSearchUtil.opensearch_end.create_index()
#populateIndex.populate_index(data=data)
#time.sleep(2)
OpenSearchUtil.opensearch_end.query_by_ingredient()
#queries.search_by_total_time(OpenSearchUtil.opensearch_end.client, OpenSearchUtil.opensearch_end.index_name, 10)


