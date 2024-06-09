from transformers import AutoModelForQuestionAnswering, AutoTokenizer, pipeline
import torch as torch

"""
This class will be used to obtain the variables from the user inputs, depending on the situation we will try and obtain the user variables
and return them
"""
debug = False

model_name = "deepset/roberta-base-squad2"
SCORE_THRESHOLD = 0.001

#Suggest me something for dinner

#region - Sentences For Identify Process State
IPI_GENERIC_QUESTION = "What are we making or cooking?"
IPI_INGREDIENT_QUESTION = "What are the ingredients?"
IPI_DURATION_QUESTION = "What is the cooking time?"
IPI_SERVINGS_QUESTION = "How many servings?"
IPI_STYLE_QUESTION = "What is the cooking or food style?"
IPI_DIFFICULTY_QUESTION = "How easy, hard or difficult is it?"
#endregion

#region - Sentences for Suggestion State
SUGI_GENERIC_QUESTION = "What do they want to make or cook?"
SUGI_OCCASION_QUESTION = "What is the occasion or event?"
SUGI_ING_QUESTION = "What ingredients do they want to use?"

#endregion

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
    
    #region - Questions for getting recipe information
    #Returns the generic information about what the user is making, if they say "I want to bake a cake" it will return cake
    def get_generic_information_ipi(self, user_input : str):
        
        question = IPI_GENERIC_QUESTION
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Returns the part of the sentence that contains the ingredients, could be like "pepperoni and cheese"
    def get_ingredient_variables_ipi(self, user_input : str):
        
        question = IPI_INGREDIENT_QUESTION
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Returns the part of the sentence that contains the pretended duration of the sentence, could return 30, or "less than half an hour"
    def get_duration_variables_ipi(self, user_input : str):
        
        question = IPI_DURATION_QUESTION
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Returns the part of the sentence that contains the number of servings, usually just returns the number
    def get_servings_variables_ipi(self, user_input : str):
        
        question = IPI_SERVINGS_QUESTION
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Returns the part of the sentence that contains the cooking style for our recipe, usually returns just the cooking style 'Mediterranean'
    def get_cooking_style_variables_ipi(self, user_input : str):
        
        question = IPI_STYLE_QUESTION
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Returns the part of the sentence that contains the cooking difficulty, could return 'easy' or 'not too difficult'
    def get_cooking_difficulty_ipi(self, user_input : str):
        
        question = IPI_DIFFICULTY_QUESTION
        
        answer = self.get_variables(question,user_input)
        return answer
    
    #Gets the generic information from the user's request to make something
    def get_ipi_prompt_information(self, user_input : str):
        
        #Ask each question to our model in order to obtain all the 
        questions = {
            'generic' : self.get_generic_information_ipi,
            'ingredients' : self.get_ingredient_variables_ipi,
            'duration' : self.get_duration_variables_ipi,
            'servings' : self.get_servings_variables_ipi,
            'style' : self.get_cooking_style_variables_ipi,
            'difficulty' : self.get_cooking_difficulty_ipi, 
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
        
        if(debug):print("SLOT FILLING: From input: {0}, Obtained:\n{1}".format(user_input,information))
        return information
    #endregion
    
    #region - Questions for getting suggestion information
    
    def get_generic_sugi(self, user_input : str):
        
        question = SUGI_GENERIC_QUESTION
        
        answer = self.get_variables(question,user_input)
        return answer
    
    def get_occasion_sugi(self, user_input : str):
        
        question = SUGI_OCCASION_QUESTION
        
        answer = self.get_variables(question,user_input)
        return answer
    
    def get_ing_sugi(self, user_input : str):
        question = SUGI_ING_QUESTION
        
        answer = self.get_variables(question,user_input)
        return answer
    
    def get_sugi_prompt_information(self, user_input : str):
        
        #Ask each question to our model in order to obtain all the 
        questions = {
            'generic' : self.get_generic_sugi,
            'occasion' : self.get_occasion_sugi,
            'ingredients' : self.get_ing_sugi
        }
        
        information = {
            'generic' : "",
            'occasion' : "",
            'ingredients' : ""

        }
        
        for type,function in questions.items():
            information[type] = function(user_input)
        
        if(debug):print("From input: {0}, Obtained:\n{1}".format(user_input,information))
        return information
    #endregion 
    
    #Debug function, to test a pair of 'question' : 'input' values
    def model_test(self, question : str, user_input : str):
        
        answer = self.get_variables(question,user_input)

###################################################### TESTING ########################################################################
#SlotFiller().get_ingredients("I would like a pizza with cheese and maybe a little tiny miniscule bit of pepperoni on it")

# sentence1 = "I would like to make a meatloaf with a cheese, ham, hazelnuts and paprika filling, it should feed 4 people and take less than 30 minutes. It should be done in a Mediterranean style, and of course, it should be easy to make as I'm not very good at cooking"
#sentence2 = "I would like to make a dessert for my daughter's birthday"
# sentence3 = "I would like to make burritos with cream cheese filling and salsa, it should feed my whole family" 
# manipulation = "How Many Servings? Carrots"
#print(SlotFiller().get_ipi_prompt_information(sentence2))