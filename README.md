# ![1740718445975](https://github.com/user-attachments/assets/6bd128bd-681e-4e93-8bd5-9cb3362de6e4) [``Knowledge Graph-Driven Memory Editing with Directional Interventions``]
## Overview
**![1740718585551](https://github.com/user-attachments/assets/24dac3ae-849f-47fd-ad86-da9b4af951bc) KGMET is a graph based edited method, taking the advantage of knowledge graph to edit LLM. (Graph4LLM)**
- It opens up a whole new direction for solving knowledge editing with Graph Neural Network (GNN).
- It improves the integration of higher-order information in the model after editing.
- It effectively blocks extraneous knowledge while ensuring editing effectiveness.
## Introduction

Model Editing methods suffer two challenges: (I) **Bad capabilities of multi-hop reasoning**: The editing approaches fails to integrate editing relevant higher-order information. (II) **Model collapse**:  Locate-then edit methods, by altering pretrained parameters, inevitably affect normal knowledge and even face thecata strophic forgetting.

![image](https://github.com/user-attachments/assets/bd3c3b4d-c5b8-4d79-8cef-8d4b77d961e0)

Previous work like rome and glame have two main challenges: **Batch delimma** Updating the weightes of a sigle mlp, which makes the methods ineffective in handing extensive editing requests; **Pattern Collapse** Glame relessly treats the embedding of knowledge as the amount of hidden state changes of LLM, which breaks the principle of magnitude consistency.

## Method

In this work, we propose *KGMET*. The framework of KGMET is shown as follows.

![image](https://github.com/user-attachments/assets/3f4ad5d0-d146-4dd3-88e3-3dd041b65c86)

KGMET incorporates **Knowledge Graph** guided **Directional Intervention** approach, with magnitude consistency criterion, avoiding *Pattern Collapse* problem, while enabling LLM to effectively improve **multi-hop reasoning** ability in batch editing scenarios. **Orthogonal constraint** is also introduced. With *SVD* and *null-space projection* technologies, it can maximally **block the irrelevant knowledge** . 

## Main experimental results
### Experimental results on ZsRE and Multi-CounterFact
![image](https://github.com/user-attachments/assets/33d3a8a8-3e9b-42e2-a4c5-2cf2700289ff)

### Multi-hop experiment in editing task on MQuAKE
![image](https://github.com/user-attachments/assets/2aefc337-a286-4ea1-8da2-1c264331fb7a)

### General ability of edited model (SST, MRPC, COLA, RTE, MMLU, NLI)
![image](https://github.com/user-attachments/assets/6f6c19b4-0a69-431a-87bc-d1190fc06782)


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
#### 1. Clone the repository
#### 2. Create a virtual environment and activate it:
   `conda create -n KGMET python=3.9`
   
   `conda activate KGMET`
#### 3. Install the required dependencies: 
    pip install -r requirements.txt
#### 4. Edit Llama3 (8B) model 
 
    python3 -m experiments.evaluate     --alg_name=KGMET     --model_name=meta-llama/Meta-Llama-3-8B-Instruct     --hparams_fname=Llama3-8B.json --ds_name=mcf  --downstream_eval_steps=5

This command runs an evaluation script for the KGMET algorithm using the Llama3-8b-instruct. Below are the explanations for each argument:

- `--alg_name=KGMET`: Specifies the name of the algorithm being used, which is KGMET in this case.
- `--model_name=meta-llama/Meta-Llama-3-8B-Instruct`: Indicates the name of the model being evaluated, here it is Llama-3-8B-Instruct.
- `--hparams_fname=Llama3-8B.json`: Points to the JSON file containing hyperparameters specific to the Llama-3-8B-Instruct model.
- `--ds_name=mcf`: Specifies the dataset name, in this case, "mcf". 
- `--downstream_eval_steps=5`: indicates that a test of general capabilities is conducted after every 5 rounds of editing.
#### 2. Summarize the results

    python summarize.py --dir_name=KGMET --runs=run_<run1>,run_<run2>

## Acknowledgment
Our code is based on  [``MEMIT``](https://github.com/kmeng01/memit.git).
