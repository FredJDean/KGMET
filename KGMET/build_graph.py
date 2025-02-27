import torch
import dgl

from dgl.nn.pytorch.conv import EGATConv
from typing import List, Dict, Literal, Optional
from transformers import PreTrainedTokenizer, PreTrainedModel

from .repr_tools import get_hidden_state
from .AlphaEdit_hparams import AlphaEditHyperParams

import torch.nn as nn
import os
import pickle


# 读取json文件并构建图
def build_graph_from_triples(
        triples: list,
        model: PreTrainedModel,
        tokenizer: PreTrainedTokenizer,
        hparams: AlphaEditHyperParams
) -> (dgl.DGLGraph(), list):

   # base_graph_dir="./graphs_mcf"
   # if not os.path.exists(base_graph_dir):
   #     os.makedirs(base_graph_dir)

   # subject_example = triples[0]['subject'] if len(triples) > 0 else "example_subject"
   # relation_example = triples[0]['relation'] if len(triples) > 0 else "example_relation"
   # graph_file_path = os.path.join(base_graph_dir, f"{subject_example}_{relation_example}_graph.bin")

  # if os.path.exists(graph_file_path):
   #     print(f"Graph found, loading from file: {graph_file_path}")
   #     graphs, node_indices, init_rel_emb = dgl.load_graphs(graph_file_path)
   #     return graphs[0], node_indices, init_rel_emb

    g = dgl.DGLGraph()
    g = g.to("cuda")

    nodes = {}
    edges = []
    node_features = []
    edge_features = []

    # 在遍历三元组之前，创建关系类型到索引的映射
    relation_types = set(triple['relation'] for triple in triples)
    relation_to_id = {rel: idx for idx, rel in enumerate(relation_types)}
    edge_type_ids = []

    init_rel_emb = []

    for idx, relation in enumerate(relation_types):
        relation_vec = get_hidden_state(model, tokenizer, hparams, relation)
        # relation_vec = torch.zeros(1600, dtype=torch.float)
        init_rel_emb.append(relation_vec)

    init_rel_emb = torch.stack(init_rel_emb).to("cuda")

    print("Iterating Triples")

    for triple in triples[:hparams.subgraph_size]:
        subject_str = triple['subject']
        relation_str = triple['relation']
        target_str = triple['target']

        subject_vec = get_hidden_state(model, tokenizer, hparams, subject_str)
        relation_vec = init_rel_emb[relation_to_id[relation_str]]
        target_vec = get_hidden_state(model, tokenizer, hparams, target_str)

        if subject_str not in nodes:
            nodes[subject_str] = subject_vec
        if target_str not in nodes:
            nodes[target_str] = target_vec

        edges.append((subject_str, target_str))
        edge_features.append(relation_vec)

        edge_type_ids.append(relation_to_id[relation_str])


    nodes_list = list(nodes.keys())
    nodes_list.sort()
    node_indices = {node: index for index, node in enumerate(nodes_list)}
    node_features = [nodes[node] for node in nodes_list]

    edges = [(node_indices[v], node_indices[u]) for u, v in edges]

    g.add_nodes(len(nodes_list))
    g.add_edges(*zip(*edges))

    g.ndata['feat'] = torch.stack(
        [n.cpu() for n in node_features]).to("cuda")
    g.ndata['id'] = torch.tensor(
        [node_indices[n] for n in nodes_list], dtype=torch.long).to("cuda")
    g.edata['r_h'] = torch.stack(
        [e.cpu() for e in edge_features]).to("cuda")
    g.edata['etype'] = torch.tensor(edge_type_ids, dtype=torch.long).to("cuda")

    g = dgl.add_self_loop(g)
    indegrees = g.in_degrees().float()
    node_norm = torch.pow(indegrees, -1)

    g.ndata['norm'] = node_norm.view(-1, 1).to("cuda")

    print("Finished building graph")

    return g, node_indices, init_rel_emb



def check_device(model):
    for name, param in model.named_parameters():
        print('Layer:', name, 'Device:', param.device)
