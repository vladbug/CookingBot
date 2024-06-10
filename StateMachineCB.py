from statemachine import StateMachine, State
from enum import Enum
import random
from models.SlotFilling import SlotFiller
from OpenSearch.query_manager import QueryManager
from dialog.Dialog import Dialog
import OpenSearch.opensearch as OpenSearchUtil
import OpenSearch.transformer as tr
import json
import pickle
import re
from models.IntentDetector import IntentDetector
from Akinator import Akinator
from sklearn.metrics.pairwise import cosine_similarity

class Acronym(Enum):
    GETCURIOSITIESINTENT = "gci"
    GREETINGINTENT = "gi"
    SELECTINTENT = "si"
    SHOWSTEPSINTENT = "ssi"
    MOREOPTIONSINTENT = "moi"
    REPEATINTENT = "ri"
    HELPINTENT = "hi"
    QUESTIONINTENT = "qi"
    MOREDETAILINTENT = "mdi"
    ADJUSTSERVINGSINTENT = "asi"
    GOTOSTEPINTENT = "gtsi"
    FALLBACKINTENT = "fi"
    PREVIOUSSTEPINTENT = "psi"
    TERMINATECURRENTTASKINTENT = "tcti"
    CHITCHATINTENT = "chit"
    COMPLETETASKINTENT = "cti"
    NONEOFTHESEINTENT = "noti"
    PAUSEINTENT = "pi"
    CANCELINTENT = "ci"
    STARTSTEPSINTENT = "startSI"
    INAPPROPRIATEINTENT = "ii"
    NOINTENT = "ni"
    SUGGESTIONSINTENT = "sugi"
    RESUMETASKINTENT = "rti"
    INGREDIENTSCONFIRMATIONINTENT = "ici"
    NEXTSTEPINTENT = "nsi"
    IDENTIFYPROCESSINTENT = "ipi"
    YESINTENT = "yi"
    SUBSTITUTIONINTENT = "subi"
    STOPINTENT = "stopI"
    AKINATORINTENT = "aki"

greetings = [
    "Hi there! How can I assist you?",
    "Hello!",
    "Hey!",
    "Hi!",
    "Howdy!",
    "Greetings!",
    "Hey there!",
    "Hiya!",
    "Hello there!",
    "Good day!"
]

class DialogManager:
    def __init__(self):
        self.state_machine = StateMachineCB(self)
        self.agent_response = ""
        self.intent_detector = IntentDetector()
    
    
    def print_msg(self, message):
        print("TaskBot: ", message)

    def process_message(self, message):
        intent = " "
        if "akinator" in message.lower():#Hardcoded intent for akinator
            intent = "AkinatorIntent"
        else:
            intent = self.intent_detector.detect_intent(self.agent_response, message)
            
        self.state_machine.send_msg(intent, message)



class StateMachineCB(StateMachine):
    greetings = State(initial=True)
    start = State()
    suggestion_state = State()
    identify_process_state = State()
    recipe_selected_state = State()
    enter_recipe_state = State()
    akinator_state = State()

    gi = greetings.to(start) | start.to(start)
    sugi = start.to(suggestion_state) | suggestion_state.to(suggestion_state) | identify_process_state.to(suggestion_state) | recipe_selected_state.to(suggestion_state)
    ipi = start.to(identify_process_state) | identify_process_state.to(identify_process_state) | suggestion_state.to(identify_process_state) | recipe_selected_state.to(identify_process_state)
    si = suggestion_state.to(recipe_selected_state) | identify_process_state.to(recipe_selected_state)
    ssi = recipe_selected_state.to(recipe_selected_state) 
    ici = recipe_selected_state.to(recipe_selected_state)
    startSI = recipe_selected_state.to(enter_recipe_state)
    tcti = enter_recipe_state.to(start)
    stopI = enter_recipe_state.to(start)
    rti = enter_recipe_state.to(enter_recipe_state)
    asi = enter_recipe_state.to(enter_recipe_state)
    gtsi = enter_recipe_state.to(enter_recipe_state) 
    subi = enter_recipe_state.to(enter_recipe_state) 
    cti =  enter_recipe_state.to(start)
    nsi = enter_recipe_state.to(enter_recipe_state)
    psi = enter_recipe_state.to(enter_recipe_state)
    yi = recipe_selected_state.to(enter_recipe_state)
    ni = recipe_selected_state.to(identify_process_state)
    aki = start.to(akinator_state)
    qi = enter_recipe_state.to(enter_recipe_state)
    ri = enter_recipe_state.to(enter_recipe_state)
    fi = enter_recipe_state.to(enter_recipe_state)

    def __init__(self, dialog_manager):
        self.dialog_manager = dialog_manager
        super(StateMachineCB, self).__init__()
        self.connect()
        self.recipes = self.load_recipes()
        self.recipe_embeddings = self.load_recipe_embeddings()
        self.slot_filler = SlotFiller()
        self.plan_llm = Dialog(self.recipes, self.recipe_embeddings)
        self.akinator = Akinator(self.recipes)
        self.curr_recipe = None
        self.recipes = []
        self.send_msg("GreetingIntent")
        
        
        
    def load_recipes(self):
        with open("./Defs/recipes_data_comp_trans.json", "r") as read_file:
            data = json.load(read_file)
        return data

    def load_recipe_embeddings(self):
        with open("./Defs/recipe_embeddings", "rb") as read_file:
            data = pickle.load(read_file)
        return data
    
    def connect(self):
        OpenSearchUtil.opensearch_end.disconnect()
        client_info = OpenSearchUtil.opensearch_end.connect()
        client = client_info[0]
        index_name = client_info[1]
        self.query_manager = QueryManager(client,index_name)

    def convert_intent(self, intent):
        return Acronym[intent.upper()].value
    
    #Function to send state transitions
    def send_msg(self, intent, message=""):
        intent = self.convert_intent(intent)
        self.send(intent, message=message)

    #Greetings state
    def on_enter_greetings(self):
        idx = random.randint(0, len(greetings) - 1)
        res = greetings[idx]
        self.dialog_manager.agent_response = res
        self.dialog_manager.print_msg(res)

    #Starting state
    def on_enter_start(self, event: str, source: State, target: State, message: str = ""):
        #print("\nEntered start from transition: {0}".format(event))
        if event == Acronym.STOPINTENT.value:
            self.dialog_manager.print_msg(explore_msg)
            return
        self.plan_llm.reset()
        
    #Recipe suggestion state
    def on_enter_suggestion_state(self, event: str, source: State, target: State, message: str = ""):
        #print("\nEntered suggestion_state from transition: {0}".format(event))
        
        #Get recipe from OpenSearch
        res = self.slot_filler.get_sugi_prompt_information(message)
        res = self.query_manager.query_generic_opensearch(res, suggestion=True)
        
        res = res["hits"]["hits"][0]
        
        #Load recipes into StateMachine
        self.curr_recipe = res["_source"]["recipe_json"]
        self.curr_recipe["id"] = res["_id"]
        
        res = suggestion_response.format(self.curr_recipe["displayName"])
        self.dialog_manager.agent_response = res
        #Print suggestion to user
        self.dialog_manager.print_msg(res)

    def on_enter_identify_process_state(self, event: str, source: State, target: State, message: str = ""):
        #print("\nEntered identify_process_state from transition: {0}".format(event))
        
        if event != Acronym.NOINTENT:
            #Get recipes (10) from Opensearch
            res = self.slot_filler.get_ipi_prompt_information(message)
            res = self.query_manager.query_generic_opensearch(res, num_results=10)
            
            self.recipes = res["hits"]["hits"]
        
        if self.recipes == []:
            self.dialog_manager.agent_response = no_recipes_left_response
            self.dialog_manager.print_msg(no_recipes_left_response)
            return
        #Load recipes into StateMachine
        recipes_names = [recipe["_source"]["recipeName"] for recipe in self.recipes]
        recipes_names = "\n".join(recipes_names)
        
        res = identify_response.format(recipes_names)
        self.dialog_manager.agent_response = res
        #Print multiple suggestions to user
        self.dialog_manager.print_msg(res)
        self.recipes = self.recipes[:3]

    #Selects the best recipe to match the user's request, when we prompt him 3 recipes we select the one we think he wants
    def best_recipe(self, msg_embedding):
        #Recipe positions
        positions = [tr.encode("I want the first one "), tr.encode("I want the second one "), tr.encode("I want the third one ")]
        
        best_recipe = None
        best_similarity = 0
        
        for i in range(len(self.recipes)):
            recipe = self.recipes[i]["_source"]
            recipe["id"] = self.recipes[i]["_id"]
            recipe_embedding = positions[i]
            similarity = cosine_similarity(msg_embedding, recipe_embedding)
            
            #Max likeliness
            if similarity > best_similarity:
                best_similarity = similarity
                best_recipe = recipe
                
        best_recipe["recipe_json"]["id"] = best_recipe["id"]
        return best_recipe["recipe_json"]
    
    #When the user has selected a recipe from our options    
    def on_enter_recipe_selected_state(self, event: str, source: State, target: State, message: str = ""):
        #print("\nEntered recipe_selected_state from transition: {0}".format(event))
        
        if event == Acronym.SELECTINTENT.value: #If the user confirmed that the recipe selected is the one
            msg_embedding = tr.encode(message)
            self.curr_recipe = self.best_recipe(msg_embedding)
            res = confirmation_response.format(self.curr_recipe["displayName"])
            self.dialog_manager.agent_response = res
            self.dialog_manager.print_msg(res)
        elif event == Acronym.INGREDIENTSCONFIRMATIONINTENT.value:
            ingrs = set()
            for ing in self.curr_recipe["ingredients"]:
                ingrs.add(ing["ingredient"])
            res = ingredients_response.format("\n".join(ingrs))
            self.dialog_manager.agent_response = res
            self.dialog_manager.print_msg(res)
            
        elif event == Acronym.SHOWSTEPSINTENT.value:
            steps = [step["stepText"] for step in self.curr_recipe["instructions"]]
            res = steps_response.format("\n".join(steps))
            self.dialog_manager.agent_response = res
            self.dialog_manager.print_msg(res)

    def extract_links(self, text):
        # Define the regex pattern for URLs
        url_pattern = r'https?://[^\s]+'
        
        # Find all matching patterns in the text
        links = re.findall(url_pattern, text)
    
        return links
    
    #PlanLLM
    def on_enter_enter_recipe_state(self, event: str, source: State, target: State, message: str = ""):
        #print("\nEntered enter_recipe_state from transition: {0}".format(event))

        if event == Acronym.YESINTENT.value or event == Acronym.STARTSTEPSINTENT.value:
            self.plan_llm.set_recipe(self.curr_recipe["id"])
            res = self.plan_llm.add_user_message("Let's begin!")
            self.dialog_manager.print_msg(res)  
            
        elif event == Acronym.GOTOSTEPINTENT.value:
            links = self.extract_links(message)
            if len(links) > 0:
                res = self.plan_llm.go_to_step_with_image(links[0])
                self.dialog_manager.agent_response = res
                self.dialog_manager.print_msg(res)
            else:
                res = self.plan_llm.go_to_step_with_text(message)
                self.dialog_manager.agent_response = res
                self.dialog_manager.print_msg(res)
            
        else:
            res = self.plan_llm.add_user_message(message)
            self.dialog_manager.agent_response = res
            self.dialog_manager.print_msg(res)
        
    
    def on_enter_aki(self, event: str, source: State, target: State, message: str = ""):
        #print("\nEntered akinator_state from transition: {0}".format(event))
        self.akinator.play()
        


#region - Answer templates

suggestion_response = """
    Sure, here's a suggestion for you to cook! Here's a recipe for you to try out:\n{0}\nIf you don't like this recipe idea, ask me again for more.
"""
identify_response = """
    I found these recipes that match what you asked for, let me know which one you prefer:\n{0}\nIf you don't like these recipe ideas, ask me again for more.
"""

confirmation_response = """
So you want to make: {0} correct?
"""

no_recipes_left_response = "I'm sorry, I couldn't find any recipes that match your request. Please be more specific."

ingredients_response = """
Here are the ingredients for the recipe you selected:\n{0}
"""

steps_response = """
Here are the steps for the recipe you selected:\n{0}
"""

explore_msg = "If you want to explore more recipes, just ask me!"
#endregion





if __name__ == "__main__":
    dialog_manager = DialogManager()
    
    
    
    def main():
        while(True):
            user_msg = input("User: ")
            dialog_manager.process_message(user_msg)
    main()