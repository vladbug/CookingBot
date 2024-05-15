from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import torch as torch

"""
This class will be used to obtain the variables from the user inputs, depending on the situation we will try and obtain the user variables
and return them
"""
debug = False

model_name = "deepset/roberta-base-squad2"
SCORE_THRESHOLD = 0.005

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
            if(debug):print("DEBUG: Answer to question: \'{0}\' with context \'{1}\'\n Returned : \'{2}\' with score: {3}\r\n".format(question, context, answer['answer'], answer['score']))
            return answer['answer']
        else:
            if(debug):print("DEBUG: Answer to question: \'{0}\' with context \'{1}\'\n Returned NULL : \'{2}\' had too low score: {3}\r\n".format(question, context, answer['answer'],answer['score']))
            return "NULL"
    
    #Returns the generic information about what the user is making, if they say "I want to bake a cake" it will return cake
    def get_generic_information(self, user_input : str):
        
        question = "What are we making or cooking?"
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Returns the part of the sentence that contains the ingredients, could be like "pepperoni and cheese"
    def get_ingredient_variables(self, user_input : str):
        
        question = "What are the ingredients?"
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Returns the part of the sentence that contains the pretended duration of the sentence, could return 30, or "less than half an hour"
    def get_duration_variables(self, user_input : str):
        
        question = "How long should it take?"
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Returns the part of the sentence that contains the number of servings, usually just returns the number
    def get_servings_variables(self, user_input : str):
        
        question = "How many servings?"
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Returns the part of the sentence that contains the cooking style for our recipe, usually returns just the cooking style 'Mediterranean'
    def get_cooking_style_variables(self, user_input : str):
        
        question = "What is the cooking or food style?"
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Returns the part of the sentence that contains the cooking difficulty, could return 'easy' or 'not too difficult'
    def get_cooking_difficulty(self, user_input : str):
        
        question = "How easy, hard or difficult is it to make?"
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Gets the generic information from the user's request to make something
    def get_recipe_prompt_information(self, user_input : str):
        
        #Ask each question to our model in order to obtain all the 
        questions = {
            'generic' : self.get_generic_information,
            'ingredients' : self.get_ingredient_variables,
            'duration' : self.get_duration_variables,
            'servings' : self.get_servings_variables,
            'style' : self.get_cooking_style_variables,
            'difficulty' : self.get_cooking_difficulty, 
        }
        
        information = {
            'generic' : "",
            'ingredients' : "",
            'duration' : "",
            'servings' : "",
            'style' : "",
            'difficulty' : "" 
        }
        
        for type,function in questions.items():
            information[type] = function(user_input)
        
        print(information)
    
    #Debug function, to test a pair of 'question' : 'input' values
    def model_test(self, question : str, user_input : str):
        
        answer = self.get_variables(question,user_input)

###################################################### TESTING ########################################################################
#SlotFiller().get_ingredients("I would like a pizza with cheese and maybe a little tiny miniscule bit of pepperoni on it")

sentence = "I would like to bake a chocolate cake for my daughter's birthday party"
#sentence = "I would like to make a dessert for my daughter's birthday"

SlotFiller().get_recipe_prompt_information(sentence)