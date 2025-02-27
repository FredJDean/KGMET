![image](https://github.com/user-attachments/assets/5fec76a4-c58b-4103-8ae3-75a403c08ac7)# KGMET
- Code for [``Knowledge Graph-Driven Memory Editing with Directional Interventions``]
- 
![image](https://github.com/user-attachments/assets/3f4ad5d0-d146-4dd3-88e3-3dd041b65c86)

## Requirements
**Our experiment is conducted in a sigle A100.**
- pytorch==1.12.1
- einops==0.4.0
- higher==0.2.1
- hydra-core==1.2.0
- transformers==4.23.1
- datasets==1.18.3
- matplotlib==3.6.1
- spacy==3.4.1
- scipy==1.9.2
- scikit-learn==1.0.2
- nltk==3.7
- dgl==1.1.2+cu118
- dglgo==0.0.2
## Quick Start
### An example for editing Llama3 (8B) on counterfact dataset using KGMET
#### 1. Edit Llama3 (8B) model 
 
    python3 -m experiments.evaluate     --alg_name=KGMET     --model_name=meta-llama/Meta-Llama-3-8B-Instruct     --hparams_fname=Llama3-8B.json --ds_name=mcf  --downstream_eval_steps=5

This command runs an evaluation script for the NSE algorithm using the Llama3-8b-instruct. Below are the explanations for each argument:

- `--alg_name=KGMET`: Specifies the name of the algorithm being used, which is KGMET in this case.
- `--model_name=meta-llama/Meta-Llama-3-8B-Instruct`: Indicates the name of the model being evaluated, here it is Llama-3-8B-Instruct.
- `--hparams_fname=Llama3-8B.json`: Points to the JSON file containing hyperparameters specific to the Llama-3-8B-Instruct model.
- `--ds_name=mcf`: Specifies the dataset name, in this case, "mcf". 
- `--downstream_eval_steps=5`: indicates that a test of general capabilities is conducted after every 5 rounds of editing.
#### 2. Summarize the results

    python summarize.py --dir_name=KGMET --runs=run_<run1>,run_<run2>

## Acknowledgment
Our code is based on  [``MEMIT``](https://github.com/kmeng01/memit.git).
