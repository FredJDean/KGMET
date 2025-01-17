import json
file_path = "./data/zsre_graph.json"
with open(file_path, 'r', encoding='utf-8') as f:
    file_data = json.load(f)

file_data_new = []
for idx, item in enumerate(file_data):
    item["case_id"] = idx
    file_data_new.append(item)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(file_data_new, f, ensure_ascii=False, indent=4)
