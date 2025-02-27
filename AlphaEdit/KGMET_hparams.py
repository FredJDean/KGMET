from dataclasses import dataclass
from typing import List, Literal

from util.hparams import HyperParams


@dataclass
class KGMETHyperParams(HyperParams):
    # Method
    model_name: str
    layers: List[int]
    layer_selection: Literal["all", "random"]
    fact_token: Literal[
        "last", "subject_first", "subject_last", "subject_first_after_last"
    ]
    v_num_grad_steps: int
    v_lr: float
    v_loss_layer: int
    v_weight_decay: float
    clamp_norm_factor: float
    kl_factor: float
    mom2_adjustment: bool
    mom2_update_weight: float

    # Module templates
    rewrite_module_tmp: str
    layer_module_tmp: str
    mlp_module_tmp: str
    attn_module_tmp: str
    layer_mlp_input: str
    ln_f_module: str
    lm_head_module: str

    # Statistics
    mom2_dataset: str
    mom2_n_samples: int
    mom2_dtype: str
    nullspace_threshold: float
    L2: float

    # gnn parameters
    gnn_fact_token_strategy: str
    gnn_dim_factor: float
    gnn_attn_drop: float
    gnn_feat_drop: float
    get_repr_layer: int
    subgraph_size: int
    gnn_weight_decay: float
    gnn_loss_layer: int
    gnn_lr: float
    factor_g: int
