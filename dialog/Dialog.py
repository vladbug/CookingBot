from models.LLM import LLM
from dialog.Recipe import Recipe
import json
import pickle
import pprint as pp
class Dialog:
    def __init__(self):
        self.recipes = self.load_recipes()
        self.embeddings = self.load_recipe_embeddings()
        self.recipe = None
        self.llm = LLM()
        self.dialog_json ={}
        self.initialize_dialog_json()

    
    def load_recipes(self): #TODO PASSAR POR PARAMETRO
        with open("./Defs/recipes_data_comp_trans.json", "r") as read_file:
            data = json.load(read_file)
        return data

    def load_recipe_embeddings(self): #TODO PASSAR POR PARAMETRO
        with open("./Defs/recipe_embeddings", "rb") as read_file:
            data = pickle.load(read_file)
        return data
    
    def reset(self):
        self.recipe = None
        self.initialize_dialog_json()

    def initialize_dialog_json(self):
        self.dialog_json = {
            "dialog_id": "1",
            "system_tone": "neutral",
            "task":{
                "recipe": {
                }
            },
            "dialog":[]
        }

    #Set the current active recipe
    def set_recipe(self, recipe_id):
        self.reset()
        recipe = self.recipes[recipe_id]
        emb = self.embeddings[recipe_id]
        self.recipe = Recipe(recipe,emb)
        self.dialog_json["task"]["recipe"]["displayName"] = recipe["displayName"]
        self.dialog_json["task"]["recipe"]["instructions"] = recipe["instructions"]
        return self.recipe
    
    def add_user_message(self, text):
        user_input = {"current_step":self.recipe.get_current_step(), "user": text}
        self.dialog_json["dialog"].append(user_input)
        response = self.llm.request(self.dialog_json)
        self.dialog_json["dialog"].pop()#Remove the last entry
        #Reintroduce it again, but with the system answer
        self.dialog_json["dialog"].append({"current_step":self.recipe.get_current_step(), "user":text,"system": response})
        return response
        

    #We always compare the text embedding with the recipe's text embedding + the image embedding
    def go_to_step_with_image(self, url):
        step = self.recipe.predict_step_with_img(url)
        step = step - 1
        self.dialog_json["dialog"].append({"current_step":step, "user": "I am currently on step " + str(step), "system": "ok"})
        return self.add_user_message("What should I do now?")

    def go_to_step_with_text(self, text):
        step = self.recipe.predict_step_with_txt(text)
        step = step - 1
        self.dialog_json["dialog"].append({"current_step":step, "user": "I am currently on step " + str(step), "system": "ok"})
        return self.add_user_message("What should I do now?")
        

    def t(self):
        self.set_recipe("4")
        self.add_user_message("Let's begin!")
        self.go_to_step_with_text("Pipe the macarons onto the parchment paper in 1\u00bd-inch (3-cm) circles, spacing at least 1-inch (2-cm) apart.")
        #self.go_to_step_with_image("https://static.wixstatic.com/media/fd9026_2278803b508a4a38b4b8dc730540d246~mv2.jpg/v1/fill/w_1000,h_1000,al_c,q_85/fd9026_2278803b508a4a38b4b8dc730540d246~mv2.jpg")
        self.add_user_message("What is the current step?")
        #self.add_user_message("go to the step where I use vanilla to incorporate it to the recipe")
        #self.add_user_message("Not that step, the step five where we use vanilla")
        #pp.pprint(self.dialog_json)
        #self.add_user_message("What is the current step?")
      
    
