import json
import OpenSearch.create_index as create_index

def load_json():
    with open("recipes_data.json", "r") as read_file:
        data = json.load(read_file)
    return data


    
data = load_json()
print(data['0']['components'])