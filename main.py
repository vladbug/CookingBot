import json
import OpenSearch.opensearch as OpenSearchUtil 
import OpenSearch.populate_index as populateIndex

def load_json():
    with open("./Defs/recipes_data.json", "r") as read_file:
        data = json.load(read_file)
    return data

data = load_json()
OpenSearchUtil.opensearch_end.disconnect()
OpenSearchUtil.opensearch_end.connect()
# TODO NAO CORRER ESTAS TRES LINHAS
# OpenSearchUtil.opensearch_end.delete_index()
# OpenSearchUtil.opensearch_end.create_index()
#populateIndex.populate_index(data=data)
OpenSearchUtil.opensearch_end.query()


