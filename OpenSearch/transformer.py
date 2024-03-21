from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from sklearn.feature_extraction.text import CountVectorizer

tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/msmarco-distilbert-base-v2")
model = AutoModel.from_pretrained("sentence-transformers/msmarco-distilbert-base-v2")

#Mean pooling - Take average of all tokens
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = input_mask_expanded.sum(1)
    sum_mask = torch.clamp(sum_mask, min=1e-9)
    return sum_embeddings / sum_mask

#Encode the text
def encode(texts):

    #Remove empty string and None strings
    texts = [t for t in texts if t and t.strip()]

  

    #Tokenize sentences
    encoded_input = tokenizer(texts, padding=True, truncation=True, return_tensors='pt')

    #Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input,return_dict=True)


    #Perform pooling. In this case, mean pooling
    embeddings = mean_pooling(model_output, encoded_input['attention_mask'])

    #Normalize the embeddings
    normalized_embeddings = F.normalize(embeddings,p=2,dim=1)

    return normalized_embeddings

#Sentences we want to encode for our embedding
#docs = ["I live in London","I live in the capital of England"] # where we will have the JSON information
#doc_emb = encode(docs)