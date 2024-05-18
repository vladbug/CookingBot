from statemachine import StateMachine, State
from enum import Enum
class Acronym(Enum):
    GETCURIOSITIESINTENT = "gci"
    GREETTINGINTENT = "gi"
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



class DialogManager(StateMachine):

    start = State(initial=True)
    suggestion_state = State()
    identify_process_state = State()
    recipe_selected_state = State()
    enter_recipe_state = State()
    current_step_state = State()
    next_step_state = State()
    previous_step_state = State()

    sugi = start.to(suggestion_state) | suggestion_state.to(suggestion_state) | identify_process_state.to(suggestion_state) | recipe_selected_state.to(suggestion_state)
    ipi = start.to(identify_process_state) | identify_process_state.to(identify_process_state) | suggestion_state.to(identify_process_state) | recipe_selected_state.to(identify_process_state)
    si = suggestion_state.to(recipe_selected_state) | identify_process_state.to(recipe_selected_state)
    ssi = recipe_selected_state.to(recipe_selected_state) 
    igi = recipe_selected_state.to(recipe_selected_state)
    startSI = recipe_selected_state.to(enter_recipe_state)
    tcti = enter_recipe_state.to(start) | current_step_state.to(start) | next_step_state.to(start) | previous_step_state.to(start)
    stopI = enter_recipe_state.to(start) | current_step_state.to(start) | next_step_state.to(start) | previous_step_state.to(start)
    rti = enter_recipe_state.to(enter_recipe_state)
    asi = enter_recipe_state.to(enter_recipe_state)
    nsi = enter_recipe_state.to(current_step_state) | current_step_state.to(next_step_state) | next_step_state.to(next_step_state) | previous_step_state.to(next_step_state)
    gtsi = enter_recipe_state.to(current_step_state) | next_step_state.to(current_step_state) | previous_step_state.to(current_step_state)
    subi = current_step_state.to(current_step_state) | next_step_state.to(next_step_state) | previous_step_state.to(previous_step_state)
    cti = current_step_state.to(start) | next_step_state.to(start) # TODO ver melhor
    psi = next_step_state.to(previous_step_state) | previous_step_state.to(previous_step_state)

    

    def __init__(self):
        super(DialogManager, self).__init__()

def convert_intent(intent):
    return Acronym[intent.upper()].value


d = DialogManager()
d.send(convert_intent("SuggestionsIntent"))
d.send(convert_intent("SuggestionsIntent"))
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
d.send(convert_intent("StopIntent"))
print(d.current_state)