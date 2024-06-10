import os
import requests
import json
"""
The PlanLLM Model will be responsible for generating text, probably in order to respond to user queries or generate answers

Given a cooking recipe, it will be able to answer questions about the recipe, such as "Next step" or "I don't have butter, what can I use" etc...
"How soft should the batter be?" 

It does not know how to handle images, we should get CLIP to handle the images

These will be called through an API that will be provided
"""

class LLM:
    def __init__(self):
        self.internal_url = 'http://10.10.255.202:5633/'
        self.external_url = "https://twiz.novasearch.org/"
        self.max_timeout = 10
        self.url = self.external_url

    def test_ping(self):
        # Make a GET request to the URL
        response = requests.get(self.url, timeout=self.max_timeout)

        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            print("GET request failed with status code:", response.status_code)


    def test_raw_post_request(self):

        url = os.path.join(self.url, "raw")

        # This is just an example that you can try to play around
        test_text = "Hi how are you today?"
        # In practice it should be in a format similar to this, (should it have the spelling mistakes?)
        test_text = "<|prompter|> You are a taskbot tasked with helping users cook recipes or DIY projects. I will give you a recipe and I want you to help me do it step by step. You should always be empathetic, honest, and should always help me. If I ask you something that does not relate to the recipe you should politely reject the request and try too get me focused on the recipe. I am unsure how to cook something or do something related to the recipe you should help me to the best of your ability. Please use a neutral tone of voice. Recipe: Test Recipe Steps: Step 1: Preheat oven to 350 degrees Step 2: Mix ingredients together Step 3: Bake for 30 minutes <|endofturn|> <|prompter|> I haven't started cooking yet. <|endofturn|> <|assistant|> ok! <|endofturn|> <|prompter|> Hello <|endofturn|> <|assistant|>"

        data = {
            "text": test_text,
            "max_tokens": 100,
            "temperature": 0.0,
            "top_p": 1,
            "top_k": -1,
        }

        # Make the POST request
        response = requests.post(url, json=data, timeout=self.max_timeout)

        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            print("POST request failed with status code:", response.status_code)


    def test_structured_post_request(self):

        url = os.path.join(self.url, "structured")

        # check this file to understand the structure of the data
        with open('dialog/example_conversation.json') as f:
            data = json.load(f)

        data = {
            "dialog": data,
            "max_tokens": 100,
            "temperature": 0.0,
            "top_p": 1,
            "top_k": -1,
        }

        # Make the POST request
        response = requests.post(url, json=data, timeout=self.max_timeout)

        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            print("POST request failed with status code:", response.status_code)

    def test(self):
        # ping
        # test_ping(internal_url)
        #self.test_ping(self.url)

        # raw
        # test_raw_post_request(internal_url)
        #self.test_raw_post_request(self.url)

        # strutured
        # test_structured_post_request(internal_url)
        self.test_structured_post_request(self.url)

    def request(self, data):

        url = os.path.join(self.url, "structured")

        data = {
            "dialog": data,
            "max_tokens": 100,
            "temperature": 0.0,
            "top_p": 1,
            "top_k": -1,
        }

        # Make the POST request
        response = requests.post(url, json=data, timeout=self.max_timeout)

        # Check if the request was successful (status code 200)
        if response.status_code != 200:
            print("POST request failed with status code:", response.status_code)
        return response.text