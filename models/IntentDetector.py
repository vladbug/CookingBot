
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import json
import os

class IntentDetector:
    def __init__(self):
        with open(os.path.join("./Defs/all_intents.json"), "r") as f:
            self.intents = json.load(f)
        self.tokenizer = AutoTokenizer.from_pretrained("NOVA-vision-language/task-intent-detector")
        self.model = AutoModelForSequenceClassification.from_pretrained("NOVA-vision-language/task-intent-detector")

    def detect_intent(self, agent_text, user_text):
        inputs = self.tokenizer.encode_plus(agent_text, user_text, return_tensors="pt")
        outputs = self.model(**inputs)
        logits = outputs.logits
        predicted_class_idx = logits.argmax().item()
        return self.intents[predicted_class_idx]
    
