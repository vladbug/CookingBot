from statemachine import StateMachine, State
from enum import Enum
import random
from models.SlotFilling import SlotFiller
from OpenSearch.query_manager import QueryManager


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
    CHITCHATINTENT = "cti"
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
    "Good day!",
    "What lovely weather we're having.",
    "I love the chinese government. CCP™",
    "Long live Xi-Jing-Ping!",
    "How do you do fellow kids, Bing Chillin, Xazioio Bing Chillin",
    "I know how to cook meth, just ask me how!",
    "Giraffes are 30 times more likely to get hit by lightning than people."
]

greeting = False

class DialogManager(StateMachine):
    greetings = State(initial=True)
    start = State()
    suggestion_state = State()
    identify_process_state = State()
    recipe_selected_state = State()
    enter_recipe_state = State()
    current_step_state = State()
    next_step_state = State()
    previous_step_state = State()


    gi = greetings.to(start) | start.to(start)
    sugi = start.to(suggestion_state) | suggestion_state.to(suggestion_state) | identify_process_state.to(suggestion_state) | recipe_selected_state.to(suggestion_state)
    ipi = start.to(identify_process_state) | identify_process_state.to(identify_process_state) | suggestion_state.to(identify_process_state) | recipe_selected_state.to(identify_process_state)
    si = suggestion_state.to(recipe_selected_state) | identify_process_state.to(recipe_selected_state)
    ssi = recipe_selected_state.to(recipe_selected_state) 
    ici = recipe_selected_state.to(recipe_selected_state)
    startSI = recipe_selected_state.to(enter_recipe_state)
    tcti = enter_recipe_state.to(start) | current_step_state.to(start) | next_step_state.to(start) | previous_step_state.to(start)
    stopI = enter_recipe_state.to(start) | current_step_state.to(start) | next_step_state.to(start) | previous_step_state.to(start)
    rti = enter_recipe_state.to(enter_recipe_state)
    asi = enter_recipe_state.to(enter_recipe_state)
    nsi = enter_recipe_state.to(current_step_state) | current_step_state.to(next_step_state) | next_step_state.to(next_step_state) | previous_step_state.to(next_step_state)
    gtsi = enter_recipe_state.to(current_step_state) | next_step_state.to(current_step_state) | previous_step_state.to(current_step_state) | current_step_state.to(current_step_state)
    subi = current_step_state.to(current_step_state) | next_step_state.to(next_step_state) | previous_step_state.to(previous_step_state)
    cti = current_step_state.to(start) | next_step_state.to(start) # TODO ver melhor
    psi = next_step_state.to(previous_step_state) | previous_step_state.to(previous_step_state)

    

    def __init__(self):
        super(DialogManager, self).__init__()
        #self._activate_initial_state()
        self.send(convert_intent("GreetingIntent"))
        self.slot_filler = SlotFiller()
        #self.query_manager = QueryManager()
      

    def on_enter_greetings(self):
        idx = random.randint(0, len(greetings) - 1)
        print(greetings[idx])

    #def on_enter_
    
    def on_enter_start(self, event: str, source: State, target: State, message: str = ""):
        print("\nEntered start from transition: {0}".format(event))
        print(message)
        #self.slot_filling.
        
    
    def on_enter_suggestion_state(self, event: str, source: State, target: State, message: str = ""):
        print("\nEntered suggestion_state from transition: {0}".format(event))
        print(message)
        # Now we need to process the message of the user, e.g "Give me a suggestion of a recipe with tomato"
        #self.slot_filling.
        res = self.slot_filler.get_sugi_prompt_information(message)
        print(res)
        #print(self.query_manager.query_by_ingredients(res['ingredients']))

        

        
        
        
        

def convert_intent(intent):
    return Acronym[intent.upper()].value

d = DialogManager()
d.send(convert_intent("SuggestionsIntent"), message="Suprise me with a recipe for dinner") 
d.send(convert_intent("SuggestionsIntent"),  message="My daughter's birthday is coming up, do you have any ideas for something for her party?")
d.send(convert_intent("SelectIntent"))
d.send(convert_intent("StartStepsIntent"))
d.send(convert_intent("ResumeTaskIntent"))
d.send(convert_intent("AdjustServingsIntent"))
d.send(convert_intent("NextStepIntent"))
d.send(convert_intent("NextStepIntent"))
d.send(convert_intent("SubstitutionIntent"))
d.send(convert_intent("PreviousStepIntent"))
d.send(convert_intent("PreviousStepIntent"))
d.send(convert_intent("GotoStepIntent"))
d.send(convert_intent("StopIntent"),message="I want to stop this")
print(d.current_state)