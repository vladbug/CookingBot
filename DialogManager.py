from statemachine import StateMachine, State
from enum import Enum
import random
from models.SlotFilling import SlotFiller
from OpenSearch.query_manager import QueryManager
from dialog.Dialog import Dialog
import OpenSearch.opensearch as OpenSearchUtil
import OpenSearch.transformer as tr
import pprint as pp


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

greeting = False

class DialogManager(StateMachine):
    greetings = State(initial=True)
    start = State()
    suggestion_state = State()
    identify_process_state = State()
    recipe_selected_state = State()
    enter_recipe_state = State()
    # current_step_state = State()
    # next_step_state = State()
    # previous_step_state = State()


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

    def __init__(self):
        super(DialogManager, self).__init__()
        #self._activate_initial_state()
        self.connect()
        self.slot_filler = SlotFiller()
        self.plan_llm = Dialog()
        self.curr_recipe = None
        self.recipes = []
        self.send_msg("GreetingIntent")
        #self.query_manager = QueryManager()
      
    def connect(self):
        OpenSearchUtil.opensearch_end.disconnect()
        client_info = OpenSearchUtil.opensearch_end.connect()
        client = client_info[0]
        index_name = client_info[1]
        self.query_manager = QueryManager(client,index_name)

    def on_enter_greetings(self):
        idx = random.randint(0, len(greetings) - 1)
        print(greetings[idx])

    #def on_enter_
    
    def on_enter_start(self, event: str, source: State, target: State, message: str = ""):
        print("\nEntered start from transition: {0}".format(event))
        self.plan_llm.reset()
        
    
    def on_enter_suggestion_state(self, event: str, source: State, target: State, message: str = ""):
        print("\nEntered suggestion_state from transition: {0}".format(event))
        res = self.slot_filler.get_sugi_prompt_information(message)
        res = self.query_manager.query_generic_opensearch(res, suggestion=True)
        res = res["hits"]["hits"][0]
        self.curr_recipe = res["_source"]["recipe_json"]
        self.curr_recipe["id"] = res["_id"]
        print(self.curr_recipe["displayName"])
     
    def on_enter_identify_process_state(self, event: str, source: State, target: State, message: str = ""):
        print("\nEntered identify_process_state from transition: {0}".format(event))
        # print(message)
        res = self.slot_filler.get_ipi_prompt_information(message)
        res = self.query_manager.query_generic_opensearch(res)
        self.recipes = res["hits"]["hits"]
        recipes_names = [recipe["_source"]["recipeName"] for recipe in self.recipes]
        print("Recipes: ", recipes_names)

    def best_recipe(self, msg_embedding):
        positions = [tr.encode("I want the first one "), tr.encode("I want the second one "), tr.encode("I want the third one ")]
        best_recipe = None
        best_similarity = 0
        for i in range(len(self.recipes)):
            recipe = self.recipes[i]["_source"]
            recipe["id"] = self.recipes[i]["_id"]
            recipe_embedding = positions[i]
            similarity = tr.cosine_similarity(msg_embedding, recipe_embedding)
            if similarity > best_similarity:
                best_similarity = similarity
                best_recipe = recipe
        best_recipe["recipe_json"]["id"] = best_recipe["id"]
        return best_recipe["recipe_json"]
        
    def on_enter_recipe_selected_state(self, event: str, source: State, target: State, message: str = ""):
        print("\nEntered recipe_selected_state from transition: {0}".format(event))
        if event == Acronym.SELECTINTENT.value:
            msg_embedding = tr.encode(message)
            self.curr_recipe = self.best_recipe(msg_embedding)
            print("Selected recipe: ", self.curr_recipe["displayName"])
        elif event == Acronym.INGREDIENTSCONFIRMATIONINTENT.value:
            ingrs = set()
            for ing in self.curr_recipe["ingredients"]:
                ingrs.add(ing["ingredient"])
            print("Ingredients: ", ingrs)
        elif event == Acronym.SHOWSTEPSINTENT.value:
            steps = [step["stepText"] for step in self.curr_recipe["instructions"]]
            print("Steps: ", steps)

    def on_enter_enter_recipe_state(self, event: str, source: State, target: State, message: str = ""):
        print("\nEntered enter_recipe_state from transition: {0}".format(event))
        if event == Acronym.STARTSTEPSINTENT.value:
            self.plan_llm.set_recipe(self.curr_recipe["id"])
        elif event == Acronym.GOTOSTEPINTENT.value:
            print("Response: " + self.plan_llm.go_to_step_with_text(message))
        else:
            print("Response: " + self.plan_llm.add_user_message(message))

    def convert_intent(self, intent):
        return Acronym[intent.upper()].value
    
    def send_msg(self, intent, message=""):
        intent = self.convert_intent(intent)
        self.send(intent, message=message)
        
        
        


d = DialogManager()
d.send_msg("SuggestionsIntent", message="Suprise me with a recipe for dinner") 
# d.send_msg("SuggestionsIntent",  message="My daughter's birthday is coming up, do you have any ideas for something for her party?")
d.send_msg("IdentifyProcessIntent", message="I want to make a cake with chocolate, that is easy to make.")
d.send_msg("SelectIntent", message="I want the second one")
d.send_msg("IngredientsConfirmationIntent",message="Can you confirm the ingredients?")
#d.send_msg("ShowStepsIntent", message="")
d.send_msg("StartStepsIntent", message="Start the recipe")
d.send_msg("PreviousStepIntent", message="previous")
#d.send_msg("GoToStepIntent", message="go to step 2" )
print("Current state: ", d.current_state)