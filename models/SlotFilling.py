from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import torch as torch

"""
This class will be used to obtain the variables from the user inputs, depending on the situation we will try and obtain the user variables
and return them
"""

model_name = "deepset/roberta-base-squad2"
SCORE_THRESHOLD = 0.01

class SlotFiller():
    
    def __init__(self):
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_name)
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.answer_pipeline = pipeline('question-answering', model = self.model, tokenizer = self.tokenizer)
        self.user_variables = []
    
    def get_variables(self, question : str, context : str):
        
        print("Processing request for: \'{0}\' for context \'{1}\'...\n".format(question,context))
        
        qa_input = {
        'context': context,
        'question': question
        }
        
        answer = self.answer_pipeline(qa_input)
        if(answer['score'] >= SCORE_THRESHOLD):
            print("DEBUG: Answer to question: \'{0}\' with context \'{1}\'\n Returned : \'{2}\'".format(question, context, answer['answer']))
            return answer
        else:
            print("DEBUG: Answer to question: \'{0}\' with context \'{1}\'\n Returned : \'{2}\' due to low score: {3}".format(question, context, 'NULL',answer['score']))
            return ""
        
    
    def get_ingredients(self, user_input : str):
        
        question = "What are the ingredients?"
        
        answer = self.get_variables(question,user_input)
        return answer
    
    def get_recipe_information(self, user_input : str):
        
        questions = [
            "What are the ingredients?",
            "What is the recipe name?"
            "How many servings?",
            
        ]
    
    def model_test(self, question : str, user_input : str):
        
        answer = self.get_variables(question,user_input)


#SlotFiller().get_ingredients("I would like a pizza with cheese and maybe a little tiny miniscule bit of pepperoni on it")

SlotFiller().model_test("How many servings?", "I want to make a pot of soup")