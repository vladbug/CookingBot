import json
import OpenSearch.create_index as indexUtil
import OpenSearch.populate_index as populateIndex

def load_json():
    with open("Defs/recipes_data.json", "r") as read_file:
        data = json.load(read_file)
    return data


data = load_json()
index = indexUtil.create_index()
if(index != None):
    #We created it, save client and index_name
    client = index[0]
    index_name = index[1]
    # client.indices.close(index = index_name, timeout=600)
    # index = indexUtil.create_index()
    indexUtil.delete_index(index[0], index[1])
    # index = indexUtil.create_index()
    # populateIndex.populate_index(data=data)
    #indexUtil.query()
    

