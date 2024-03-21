import json
import OpenSearch.opensearch as OpenSearchUtil 
import OpenSearch.populate_index as populateIndex

def load_json():
    with open("./Defs/recipes_data.json", "r") as read_file:
        data = json.load(read_file)
    return data

# client,index_name = indexUtil.connect()
# res = client.indices.close(index = index_name, timeout=600)
# print(res)
#client,index_name = indexUtil.connect()
data = load_json()
#index = indexUtil.create_index(client)
#if(index != None):

    #indexUtil.delete_index(index[0], index[1])
    #index = indexUtil.create_index(client)ls
    #populateIndex.populate_index(data=data)
OpenSearchUtil.opensearch_end.disconnect()
OpenSearchUtil.opensearch_end.connect()
#populateIndex.populate_index(data=data)
#OpenSearchUtil.opensearch_end.create_index()
#OpenSearchUtil.opensearch_end.delete_index()
OpenSearchUtil.opensearch_end.query()
    

