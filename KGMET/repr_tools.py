"""
Contains utilities for extracting token representations and indices
from string templates. Used in computing the left and right vectors for ROME.
"""

from copy import deepcopy
import torch
from typing import List, Literal, Optional
from transformers import PreTrainedTokenizer, PreTrainedModel
from .AlphaEdit_hparams import AlphaEditHyperParams

from util import nethook


def get_average_hidden_state(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    hparams: AlphaEditHyperParams,
    text: str,
) -> torch.Tensor:
    """
    Takes a string input, tokenizes it, feeds it to the transformer model, and returns 
    the averaged hidden states from the specified layer.

    :param model: PreTrainedModel, a pre-trained transformer model
    :param tokenizer: PreTrainedTokenizer, a tokenizer corresponding to the transformer model
    :param text: str, a string that we want to feed into the model
    :param layer: int, the layer number from which we want to extract the hidden states
    :return: torch.Tensor, the average hidden states from the specified layer
    """

    # Tokenize the input text
    inputs = tokenizer(text, return_tensors="pt")

    # Transfer input tensors to the same device as the model
    inputs = {name: tensor.to(model.device) for name, tensor in inputs.items()}

    # We need to specify which module's outputs we are hooking
    module_template = hparams.layer_module_tmp
    layer = hparams.get_repr_layer
    module_name = module_template.format(layer)

    # Initialize the nethook Trace
    with torch.no_grad():
        with nethook.Trace(model, layer=module_name) as tr:
            model(**inputs)
            layer_output = tr.output

    layer_output = layer_output[0] if type(
        layer_output) is tuple else layer_output

    # Calculate the mean across all tokens
    layer_output_mean = torch.mean(layer_output, dim=1)
    layer_output_mean = torch.squeeze(layer_output_mean)

    return layer_output_mean


def get_hidden_state(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    hparams: AlphaEditHyperParams,
    text: str,
    subtoken: Optional[str] = "last",
) -> torch.Tensor:
    """
    Extract the hidden output vector of a specific layer from a string.

    Args:
    model (PreTrainedModel): The loaded pre-trained model
    tokenizer (PreTrainedTokenizer): The tokenizer of the loaded pre-trained model
    text (str): The input string
    layer (int): The index of the layer
    subtoken (str): Represents the type of subword to extract, which can be "last" or "first_after_last" or "avg"

    Returns:
    torch.Tensor: The hidden output vector of the specific layer
    """
    
    if hparams.gnn_fact_token_strategy != "last":
        if hparams.gnn_fact_token_strategy == "avg" or subtoken == "avg":
            return get_average_hidden_state(
                model=model,
                tokenizer=tokenizer,
                hparams=hparams,
                text=text,
            )

    context_templates = ["{}"]
    words = [text]
    module_template = hparams.layer_module_tmp
    track = "out"

    idxs = get_words_idxs_in_templates(
        tokenizer, context_templates, words, subtoken)
    hidden_states = get_reprs_at_idxs(
        model=model,
        tokenizer=tokenizer,
        contexts=[context_templates[0].format(words[0])],
        idxs=idxs,
        layer=hparams.get_repr_layer,
        module_template=module_template,
        track=track,
    )

    if isinstance(hidden_states, dict):
        hidden_states = hidden_states["out"]

    hidden_states = hidden_states.view(-1)

    if hparams.gnn_fact_token_strategy == "composite_norm":
        avg_feat = get_average_hidden_state(
            model=model,
            tokenizer=tokenizer,
            hparams=hparams,
            text=text,
        )

        avg_feat = avg_feat*hidden_states.norm()/avg_feat.norm()
        hidden_states = (hidden_states+avg_feat)/2.0

    if hparams.gnn_fact_token_strategy == "composite":
        avg_feat = get_average_hidden_state(
            model=model,
            tokenizer=tokenizer,
            hparams=hparams,
            text=text,
        )

        hidden_states = (hidden_states+avg_feat)/2.0

    return hidden_states


def get_reprs_at_word_tokens(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    context_templates: List[str],
    words: List[str],
    layer: int,
    module_template: str,
    subtoken: str,
    track: str = "in",
) -> torch.Tensor:
    r"""
    Retrieves the last token representation of `word` in `context_template`
    when `word` is substituted into `context_template`. See `get_last_word_idx_in_template`
    for more details.
    """

    idxs = get_words_idxs_in_templates(
        tokenizer, context_templates, words, subtoken)
    return get_reprs_at_idxs(
        model=model,
        tokenizer=tokenizer,
        contexts=[context_templates[i].format(
            words[i]) for i in range(len(words))],
        idxs=idxs,
        layer=layer,
        module_template=module_template,
        track=track,
    )


def get_words_idxs_in_templates(
    tokenizer: PreTrainedTokenizer,
    context_templates: List[str],
    words: List[str],
    subtoken: str
) -> List[List[int]]:
    r"""
    Given list of template strings, each with *one* format specifier
    (e.g. "{} plays basketball"), and words to be substituted into the
    template, computes the post-tokenization index of their last tokens.

    We use left-padding so the words idxs are negative numbers.
    """

    assert all(
        tmp.count("{}") == 1 for tmp in context_templates
    ), "We currently do not support multiple fill-ins for context"

    prefixes_len, words_len, suffixes_len, inputs_len = [], [], [], []
    for i, context in enumerate(context_templates):
        prefix, suffix = context.split("{}")
        prefix_len = len(tokenizer.encode(prefix))
        prompt_len = len(tokenizer.encode(prefix + words[i]))
        input_len = len(tokenizer.encode(prefix + words[i] + suffix))
        prefixes_len.append(prefix_len)
        words_len.append(prompt_len - prefix_len)
        suffixes_len.append(input_len - prompt_len)
        inputs_len.append(input_len)

    # Compute indices of last tokens
    if subtoken == "last" or subtoken == "first_after_last":
        return [
            [
                prefixes_len[i]
                + words_len[i]
                - (1 if subtoken == "last" or suffixes_len[i] == 0 else 0)
            ]
            # If suffix is empty, there is no "first token after the last".
            # So, just return the last token of the word.
            for i in range(len(context_templates))
        ]
    elif subtoken == "first":
        return [[prefixes_len[i] - inputs_len[i]] for i in range(len(context_templates))]
    else:
        raise ValueError(f"Unknown subtoken type: {subtoken}")


def get_reprs_at_idxs(
    model: PreTrainedModel,
    tokenizer: PreTrainedTokenizer,
    contexts: List[str],
    idxs: List[List[int]],
    layer: int,
    module_template: str,
    track: Optional[Literal["in", "out", "both"]] = "in",
) -> torch.Tensor:
    r"""
    Runs input through model and returns averaged representations of the tokens
    at each index in `idxs`.
    """

    def _batch(n):
        for i in range(0, len(contexts), n):
            yield contexts[i: i + n], idxs[i: i + n]

    assert track in {"in", "out", "both"}
    both = track == "both"
    tin, tout = (
        (track == "in" or both),
        (track == "out" or both),
    )
    module_name = module_template.format(layer)
    to_return = {"in": [], "out": []}

    def _process(cur_repr, batch_idxs, key):
        nonlocal to_return
        cur_repr = cur_repr[0] if type(cur_repr) is tuple else cur_repr
        if cur_repr.shape[0] != len(batch_idxs):
            cur_repr = cur_repr.transpose(0, 1)
        for i, idx_list in enumerate(batch_idxs):
            to_return[key].append(cur_repr[i][idx_list].mean(0))

    for batch_contexts, batch_idxs in _batch(n=128):
        contexts_tok = tokenizer(batch_contexts, padding=True, return_tensors="pt").to(
            next(model.parameters()).device
        )

        with torch.no_grad():
            with nethook.Trace(
                module=model,
                layer=module_name,
                retain_input=tin,
                retain_output=tout,
            ) as tr:
                model(**contexts_tok)

        if tin:
            _process(tr.input, batch_idxs, "in")
        if tout:
            _process(tr.output, batch_idxs, "out")

    to_return = {k: torch.stack(v, 0)
                 for k, v in to_return.items() if len(v) > 0}

    if len(to_return) == 1:
        return to_return["in"] if tin else to_return["out"]
    else:
        return to_return["in"], to_return["out"]
