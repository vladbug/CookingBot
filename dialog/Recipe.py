from models.Clip import CLIPClass
import pickle
import pprint as pp

"""
This class will save a recipe to be used with the LLM, it will keep track of the current step we're on
Change recipe steps, and even try to predict the next step from a given embedding
"""

class Recipe:
    def __init__(self, data, embeddings):
        self.data = data
        self.embeddings = embeddings
        self.clip = CLIPClass()
        self.current_step = 0 

    def go_to_next_valid_step(self):
        steps = self.data['instructions']
        while steps[self.current_step]['stepText'] == "":
            self.current_step += 1
    
    def get_current_step(self):
        return int(self.current_step)
    
    def predict_step(self, embedding ):
        steps_embeddings = self.embeddings['steps_embeddings']
        max_score = 0
        best_step = ""
        
        #Iterate all the step embeddings for the recipe
        for step in steps_embeddings:
            img_embedding = steps_embeddings[step]['img_embedding']
            txt_embedding = steps_embeddings[step]['text_embedding']
            if img_embedding is None:
                img_score = 0
            else:
                img_score = self.clip.get_similarity(embedding, img_embedding)
            
            #Compare the embedding similarity
            score = self.clip.get_similarity(embedding, txt_embedding) + img_score
            if score > max_score:
                max_score = score
                best_step = step
                
        self.current_step = best_step
        print("changed the current step to: ", best_step)
        return int(best_step)
    
    def predict_step_with_txt(self, text):
        text_embedding = self.clip.get_text_embedding(text)
        return self.predict_step(text_embedding)
    
    def predict_step_with_img(self, url):
        img_embedding = self.clip.get_image_embedding(url)
        return self.predict_step(img_embedding)
    
        
# clip = CLIPClass()
# data = pickle.load(open("Defs/recipe_embeddings", "rb"))
# Recipe(None, data["4"]).predict_step(clip.get_image_embedding("https://static.wixstatic.com/media/fd9026_2278803b508a4a38b4b8dc730540d246~mv2.jpg/v1/fill/w_1000,h_1000,al_c,q_85/fd9026_2278803b508a4a38b4b8dc730540d246~mv2.jpg"))