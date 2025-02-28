import json
import os
from openai import OpenAI
import openai
# few shot
examples = (
    "Here are some examples of how to extract subject and relation:\n\n"
    "Example 1:\n"
    "Question: Who is Prince Andrew of Greece and Denmark's mother?\n"
    "Answer: (Prince Andrew of Greece and Denmark; mother)\n\n"

    "Example 2:\n"
    "Question: Who is Queen Elizabeth II's mother?\n"
    "Answer: (Queen Elizabeth II; mother)\n\n"

    "Example 3:\n"
    "Question: Who is Albert Einstein's wife?\n"
    "Answer: (Albert Einstein; wife)\n\n"

    "Example 4:\n"
    "Question: Who is Barack Obama's mother?\n"
    "Answer: (Barack Obama; mother)\n\n"
)
client = OpenAI(
    api_key="your api key",
    base_url="your base url",
)
#
# print(completion.model_dump_json())

#openai.api_key ="your api key"
#openai.base_url= "your base url"

dataset_path = "./data/zsre_mend_eval.json"

with open(dataset_path, 'r') as file:
    dataset = json.load(file)

#dataset = dataset[0:2000]

def generate_relationship_for_prompt(data, max_retries=3):
    results = []
    for entry in data:
        prompt = entry['src']
        # context = entry['context']

        # Prepare the context into a single string
        # context_text = "\n".join(context)

        # Construct the prompt for extracting subject, relation, and object
        full_prompt = (
            "Given the following Question, extract the main subject, relation in the format (subject; relation):\n"
            "Please respond **ONLY** with the relationship in the format: (subject; relation), without any other text.\n"
            f"{examples}\n\n"
            f"Question: {prompt}\n\n"
        )

        # Call OpenAI GPT-4 API to generate the relationship
        retries = 0
        while retries < max_retries:
            response = client.chat.completions.create(
                model="qwen-plus",  # you can also call gpt series all deepseek-r1, which may obtain better results.
                messages=[
                    {'role': 'user', 'content': full_prompt}],
                max_tokens=100
            )
        # response = openai.completions.create(
        #     model="qwen-plus",
        #     prompt=full_prompt,
        #     max_tokens=100,  # Adjust based on your needs
        #     temperature=0.5
        # )

            # Extract the response and print the result
            generated_text = response.choices[0].message.content

            # Assume the output will be in the form of (subject, relation, object)
            try:
                # Attempt to parse the response as a triple
                triple = generated_text.strip("()").split(";")
                if len(triple) == 2:
                    subject, relation = triple
                    results.append({
                        "subject": subject.strip(),
                        "relation": relation.strip()
                    })
                    break  # Valid triple found, exit the loop
                else:
                    raise ValueError(f"Generated text is not in the expected format: {generated_text}")
            except Exception as e:
                retries += 1
                print(f"Error parsing output (attempt {retries}): {generated_text}")
                if retries == max_retries:
                    print(f"Max retries reached for prompt: {prompt}")
                    raise e
        # Print the result
        print(f"Prompt: {prompt}")
        print(f"Generated Relationship: {generated_text}")
        print("-" * 60)

    with open('data/generated_relationships.json', 'w') as f:
        json.dump(results, f, indent=4)

generate_relationship_for_prompt(dataset)
