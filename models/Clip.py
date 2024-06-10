
from PIL import Image
import requests
import torch

from PIL import Image
import requests
import torch
from transformers import CLIPProcessor, CLIPModel


"""
The CLIP enconder will be responsible for encoding both text and images.
The main difference is in the text encoder, where it will encode the text in a way that we can
compute the similarity between the images and the text, since it encondes text as a visual representantion

model.get_text_features -> Returns the encoder responsible for encoding text
model.get_img_features -> Returns the encoder responsible for encoding images

The CLIP Score will return us the similarity between image-text prompts

Uses:
Index the images, index the steps as if they were an image/caption

Somar embeddings (o prof. n sabe se isto funciona), se tiveres um embedding de uma imagem e o embedding de "com frango" ele em teoria
vai procurar por resultados que tenham em consideração a imagem e o texto de "com frango"
"""

class CLIPClass():
     
    def __init__(self) -> None:
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        self.model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)

    def get_image_embedding(self, url:str):
        image = Image.open(requests.get(url, stream=True).raw)
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():        
            embeddings = self.model.get_image_features(**inputs)
        embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        return embeddings.cpu()

    def get_text_embedding(self, text:str):
        inputs = self.processor(text=text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            embeddings = self.model.get_text_features(**inputs)
        embeddings = embeddings / embeddings.norm(dim=-1, keepdim=True)
        return embeddings.cpu()
    
    def similarity_score_txt_img(self, text:str, url:str):
        image = self.get_image_embedding(url)
        text = self.get_text_embedding(text)
        similarity = image @ text.T
        return similarity

    def similarity_score_img_img(self, url1:str, url2:str):
        image1 = self.get_image_embedding(url1)
        image2 = self.get_image_embedding(url2)
        similarity = image2 @ image1.T
        return similarity

    def combine_img_txt(self, text:list[str], url:str):
        combined_embedding = self.get_image_embedding(url)
        for t in text:
            text_embedding = self.get_text_embedding(t)
            combined_embedding += text_embedding
            combined_embedding = combined_embedding / combined_embedding.norm(dim=-1, keepdim=True)
        return combined_embedding
    
    def combine_txt_txt(self, text:list[str]):
        combined_embedding = None
        
        for t in text:
            if(t.strip() != ""):#If the text isn't ""
                if len(t) > 77:#If the length of this text is over the embedding limit of 77 tokens:
                    all_tokens = t.split(" ")#Split the tokens yet again
                    
                    text_embeddings_commulative = None
                    input_txt = ""
                    
                    for token in all_tokens:#For each split token
                        
                        if((len(input_txt) + len(token)) > 77):#Add them one by one, and check if they go over the limit
                            if(text_embeddings_commulative == None):
                                text_embeddings_commulative = self.get_text_embedding(input_txt)
                            else:
                                text_embeddings_commulative += self.get_text_embedding(input_txt)
                                
                            input_txt = token
                        else:#They don't go over the limit, just add them to the input_txt variable
                            input_txt += " {0}".format(token)
                            
                    if input_txt != "":#Just check if there was any tokens left over
                        text_embeddings_commulative += self.get_text_embedding(input_txt)

                    text_embedding = text_embeddings_commulative
                    
                else:
                    text_embedding = self.get_text_embedding(t)
                    
                if combined_embedding is None:
                    combined_embedding = text_embedding
                else:
                    combined_embedding += text_embedding
                combined_embedding = combined_embedding / combined_embedding.norm(dim=-1, keepdim=True)
        return combined_embedding
    
    def get_similarity(self, embedding1, embedding2):
        similarity = embedding1 @ embedding2.T
        return similarity
    
