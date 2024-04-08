
from transformers import AutoTokenizer, AutoModelForTokenClassification

def get_ing_from_sentence(text):
    tokenizer = AutoTokenizer.from_pretrained("chambliss/distilbert-for-food-extraction")
    model = AutoModelForTokenClassification.from_pretrained("chambliss/distilbert-for-food-extraction")


    # Tokenize input text
    inputs = tokenizer(text, return_tensors="pt")

    # Make predictions
    outputs = model(**inputs)

    # Decode the tokenized input to get the original words
    decoded_tokens = tokenizer.decode(inputs['input_ids'][0])

    # Split the decoded tokens to get individual words
    original_words = decoded_tokens.split()

    # Get the predicted class labels
    predicted_class_indices = outputs.logits.argmax(-1)[0]

    # Create a list to store words with label 0
    parse_ingredient = []

    # Iterate over the words and their predicted labels
    for word, label in zip(original_words, predicted_class_indices):
        if word != '[CLS]' and word != '[SEP]':
            if label.item() == 0:  # Check if the label is 0
                parse_ingredient.append(word)
    return parse_ingredient
