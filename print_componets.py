from transformers import AutoModelForCausalLM

#model_name = "openai-community/gpt2-xl"
#model_name = "EleutherAI/gpt-j-6b"
model_name = "meta-llama/Meta-Llama-3-8B-Instruct"
model = AutoModelForCausalLM.from_pretrained(model_name)

def print_layers(model, prefix=""):
    for name, module in model.named_children():
        new_prefix = f"{prefix}.{name}" if prefix else name
        if len(list(module.children())) > 0:
            print_layers(module, new_prefix)
        else:
            print(f"{new_prefix}")

print_layers(model.model)
print(model.config.hidden_size)
