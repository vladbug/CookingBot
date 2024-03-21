import opensearchpy
import pprint as pp
def populate_index(data):
    #pp.pprint(document_sample)
    
    #Set recipe name
    index = 0
    while True:
        try:
            print(data[str(index)]["displayName"])
            index += 1
        except KeyError:
            print("Finished file")
            break
            
        
        

document_sample = {
    "recipeName": '',
    "prepTimeMinutes": 0,
    "cookTimeMinutes": 0,
    "totalTimeMinutes": 0,
    "difficultyLevel": '',
    "images": '',
    "videos": '', #complex object with title and url
    "tools": '',
    "cuisines": '',
    "courses": '',
    "diets": '',
    "ingredients": '',
}


#  "properties":{
#      "cuisines" : { #Array of cuisine types, "mexican", "Asian" etc..., [str]
#      "type" : "text" 
#      },
#      "courses" : { #Array of course types, "main" "breakfast" "sides" etc..., [str]
#          "type" : "text"
#      },
#      "diets" : { #Array of diet types, "vegan" etc... [str]
#          "type" : "text"
#      },
#      "ingredients" : { #Array of ingredient names, didn't save quantity cos that can be loaded later, [str]
#          "type" : "text", 
#      },