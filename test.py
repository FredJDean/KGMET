from transformers import LlamaForCausalLM, AutoTokenizer
import torch


pt_file_path = '/workspace/AlphaEdit/post_edit_hs_memit.pt'


model = LlamaForCausalLM.from_pretrained('meta-llama/Meta-Llama-3-8B-Instruct')
model_resume = torch.load(pt_file_path)

model.load_state_dict(model_resume)

tokenizer = AutoTokenizer.from_pretrained('meta-llama/Meta-Llama-3-8B-Instruct')

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

input_text = "Hello, how can I help you today?"
inputs = tokenizer(input_text, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model.generate(**inputs, max_length=50)

generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(generated_text)
