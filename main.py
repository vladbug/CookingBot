import json
import OpenSearch.create_index as indexUtil
import OpenSearch.populate_index as populateIndex

def load_json():
    with open("Defs/recipes_data.json", "r") as read_file:
        data = json.load(read_file)
    return data


    
data = load_json()
index = indexUtil.create_index()
populateIndex.populate_index(data=data)
if(index != None):
    #We created it, save client and index_name
    client = index[0]
    index_name = index[1]
    

