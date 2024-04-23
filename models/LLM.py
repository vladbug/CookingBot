from transformers import AutoTokenizer, AutoModelForCausalLM
import pprint as pp

class LLM():
    def __init__(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained("NOVA-vision-language/PlanLLM")
        self.model = AutoModelForCausalLM.from_pretrained("NOVA-vision-language/PlanLLM")

    def t():
        # Instantiate the LLM class
        llm_model = LLM()

        # Input text
        input_text = "Once upon a time, in a land far, far away, there lived a brave knight."

        # Tokenize input text
        input_ids = llm_model.tokenizer.encode(input_text, return_tensors="pt")

        # Generate text
        output = llm_model.model.generate(input_ids, max_length=100, num_return_sequences=1)

        # Decode the generated output
        generated_text = llm_model.tokenizer.decode(output[0], skip_special_tokens=True)
        pp.print(generated_text)

LLM().t()