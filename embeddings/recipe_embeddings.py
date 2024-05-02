from models.Clip import CLIPClass
import pickle
import re

class RecipesEmbeddings:
    def __init__(self, recipes):
        self.model = CLIPClass()
        self.recipes = recipes  
        self.recipe_embedding = {}

    def compute_step_text_embeddings(self, step):
        step_txts = re.split(r'[.!?;]', step)
        return self.model.combine_txt_txt(step_txts)
    
    def compute_step_img_embeddings(self, images):
        if images == []:
            return None
        url = images[0]["url"]
        print(url)
        return self.model.get_image_embedding(url)
        
    def compute_embeddings(self):
        for recipe_id in range(len(self.recipes)):
            recipe_id = str(recipe_id)
            recipe = self.recipes[recipe_id]
            recipe_steps = recipe["instructions"] #'stepImages' length == 0 ent n ha imagens
            #Iterate all the recipe steps
            steps_embeddings = {}
            for step in recipe_steps:
                images = step["stepImages"]
                text = step["stepText"]
                print(text)
                text_embedding = self.compute_step_text_embeddings(text)
                img_embedding = self.compute_step_img_embeddings(images)
                step_id = step["stepNumber"]
                steps_embeddings[str(step_id)] = {
                        "text_embedding": text_embedding,
                        "img_embedding": img_embedding
                }

            
            self.recipe_embedding[recipe_id] =  {
                    "steps_embeddings": steps_embeddings
                    }
        return self.recipe_embedding
    
    def save_embeddings(self, path):
        with open(path, 'wb') as f:
            pickle.dump(self.recipe_embedding, f)



        

    
    
