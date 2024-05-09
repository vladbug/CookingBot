
from PIL import Image
import requests
import torch
import pprint as pp

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
    
#region - Test urls
# url = "https://m.media-amazon.com/images/S/alexa-kitchen-msa-na-prod/recipes/tasty/b2398f42037962e29f0dffe1e4f327b27bee63635f6e721e14656cc5fe0b8552.jpg"
# url1 = "https://www.framatome.com/app/uploads/2023/10/framatome-space-header-1440x0-c-center.jpg"
# url2 ="https://m.media-amazon.com/images/S/alexa-kitchen-msa-na-prod/recipes/thekitchn/2d41442dc2f9b4584c648cc52b08146ffde2e59f28f3e5c4574f812ba2f5636b.jpg"
# print(CLIPClass().similarity_score_img_img(url1,url2))
# url1 = "https://as2.ftcdn.net/v2/jpg/00/18/66/99/1000_F_18669964_Txz4BS0OErzj9v9DHM3N51d8yFVa85dR.jpg"
url2 = "https://img.etimg.com/thumb/msid-95423731,width-650,height-488,imgsize-56196,resizemode-75/tomatoes-canva.jpg"
url3 = "https://m.media-amazon.com/images/S/alexa-kitchen-msa-na-prod/recipes/wholefoods/14f9645d498dc9d1670ac5a1e465f033003014bce943e90955ec2ac3f26ef79b.jpg"
url4 = "https://m.media-amazon.com/images/S/alexa-kitchen-msa-na-prod/recipes/seriouseats/2a8b13b2411b6cea820bc206842a31d2a8a5d7d90dad62243e177077a6719151.jpg"

# print(CLIPClass().similarity_score_img_img(url2,url3))
# print(CLIPClass().similarity_score_img_img(url2,url4))
# pear_comb = CLIPClass().combine_img_txt(["egg"],url3)
# tom_comb = CLIPClass().combine_img_txt(["tomato","red onion","salt"],url4)

# print(CLIPClass().get_image_embedding(url2) @ pear_comb.T)
# print(CLIPClass().get_image_embedding(url2) @ tom_comb.T)

#print(CLIPClass().similarity_score_txt_img("tomato","https://m.media-amazon.com/images/S/alexa-kitchen-msa-na-prod/recipes/simplyrecipes/ca8af795572430afc9f20a9f42ba36da8bd11edd3e1bdff91bdd39aa279fd4c5.jpg"))
#endregion