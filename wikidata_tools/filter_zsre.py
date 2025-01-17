import json

# 加载第一个和第二个文件
file_1_path = '../data/zsre_mend_eval.json'
file_2_path = 'zsre_graph.json'

# 读取文件
with open(file_1_path, 'r', encoding='utf-8') as f:
    file_1_data = json.load(f)

with open(file_2_path, 'r', encoding='utf-8') as f:
    file_2_data = json.load(f)

# 用来存储过滤后的第一个文件和第二个文件的条目
filtered_file_1_data = []
filtered_file_2_data = []

# 遍历第二个文件，检查 tripes 的长度
for idx, item in enumerate(file_2_data):
    triples_length = len(item['triples'])

    # 如果 triples 长度大于等于10，才会保留该条目
    if triples_length >= 10:
        filtered_file_1_data.append(file_1_data[idx])
        filtered_file_2_data.append(item)

# 将过滤后的文件写入新的文件
with open('filtered_zsre_mend_eval.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_file_1_data, f, ensure_ascii=False, indent=4)

with open('filtered_zsre_graph.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_file_2_data, f, ensure_ascii=False, indent=4)

print("过滤后的数据已经写入 'filtered_file_1.json' 和 'filtered_file_2.json'.")
