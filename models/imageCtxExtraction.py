from transformers import ViTFeatureExtractor, ViTForImageClassification
from PIL import Image
import requests
import torch
import pprint as pp

class ImageExtractor():
    
    def __init__(self):
        self.feature_extractor = ViTFeatureExtractor.from_pretrained('google/vit-base-patch16-384')
        self.prediction_model = ViTForImageClassification.from_pretrained('google/vit-base-patch16-384')        
    
    # def predict_image(self,url:str | None, image : Image.Image | None):
    #     if(url != None):
    #         input_image = self.retrieveImage(url)
    #     if(image != None):
    #         input_image = image
            
    #     #Extracts features from the image, such as shapes, vertical lines etc...
    #     inputs = self.feature_extractor(images=input_image, return_tensors="pt")
    #     #Feeds it to the prediction model
    #     outputs = self.prediction_model(**inputs)
    #     logits = outputs.logits

    #     #The model predicts one of the 1000 ImageNet classes
    #     predicted_class_idx = logits.argmax(-1).item()
    #     predicted_class_idx = torch.topk(logits.flatten(), 5).indices.tolist()
    #     pp.pprint([self.prediction_model.config.id2label[i] for i in predicted_class_idx])
    
    # def get_text_similarity(self, text : str | list[str], url:str | None, image : Image.Image | None):
    #     if(url != None):
    #         input_image = self.retrieveImage(url)
    #     if(image != None):
    #         input_image = image
            
    #     inputs = processor(text=["a photo of a cat", "a photo of a dog"], images=image, return_tensors="pt", padding=True)

    #     outputs = model(**inputs)
    #     logits_per_image = outputs.logits_per_image  # this is the image-text similarity score
    #     probs = logits_per_image.softmax(dim=1)
    
    #Returns a PIL image given a URL 
    def retrieveImage(self, url : str):
        image = Image.open(requests.get(url, stream=True).raw)
        return image
    
    
        




#ImageExtractor().test_function("https://m.media-amazon.com/images/S/alexa-kitchen-msa-na-prod/recipes/thekitchn/4865e5eb3dbe3b8933ebd1f2c4a12bd1e73192095c102bdcf33635c59a815165.jpg")

from PIL import Image
import requests
import torch
from transformers import CLIPProcessor, CLIPModel

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
        return embeddings

    def get_text_embedding(self, text:str):
        inputs = self.processor(text=text, return_tensors="pt").to(self.device)
        with torch.no_grad():
            embeddings = self.model.get_text_features(**inputs)
        return embeddings
    
url_cat = "https://m.media-amazon.com/images/S/alexa-kitchen-msa-na-prod/recipes/thekitchn/4865e5eb3dbe3b8933ebd1f2c4a12bd1e73192095c102bdcf33635c59a815165.jpg"

CLIPClass().get_text_embedding("a photo of a cat")
    