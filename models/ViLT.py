from transformers import ViltProcessor, ViltForQuestionAnswering, AutoTokenizer, AutoConfig
import requests
from PIL import Image

"""
(Pointless since we have CLIP)

The ViLT model will allow us to query an image through text, we can ask questions about the visual elements in the image
"""


class ViLT():
    def __init__(self) -> None:
        model_path = "dandelin/vilt-b32-finetuned-vqa"
        config = AutoConfig.from_pretrained(model_path,  output_hidden_states=True, output_attentions=True)  
        self.processor = ViltProcessor.from_pretrained(model_path)
        self.model = ViltForQuestionAnswering.from_pretrained(model_path, config=config)

    def get_image_text(self, img_url : str):
        image = Image.open(requests.get(img_url, stream=True).raw)
        question = "this has corn?"
        VQ_encoding = self.processor(image, question, return_tensors="pt")
        outputs = self.model(**VQ_encoding, return_dict = True)
        logits = outputs.logits
        idx = logits.argmax(-1).item()
        print("Predicted answer:", self.model.config.id2label[idx])

ViLT().get_image_text("https://m.media-amazon.com/images/S/alexa-kitchen-msa-na-prod/recipes/thekitchn/4865e5eb3dbe3b8933ebd1f2c4a12bd1e73192095c102bdcf33635c59a815165.jpg")