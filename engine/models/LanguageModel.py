from __future__ import annotations

from typing import List, Union

import torch
from torch.utils.hooks import RemovableHandle
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoTokenizer,
    BatchEncoding,
    PretrainedConfig,
    PreTrainedModel,
    PreTrainedTokenizer,
)

from .AbstractModel import AbstractModel


class LanguageModel(AbstractModel):
    def __init__(self, *args, **kwargs) -> None:
        self.config: PretrainedConfig = None
        self.tokenizer: PreTrainedTokenizer = None
        self.meta_model: PreTrainedModel = None

        self.local_model: PreTrainedModel = None

        super().__init__(*args, **kwargs)

    def register_increment_hook(self, hook) -> RemovableHandle:
        return self.local_model.register_forward_hook(hook)

    def load_meta(self, repoid_or_path, *args, **kwargs) -> PreTrainedModel:
        self.config = AutoConfig.from_pretrained(repoid_or_path, *args, **kwargs)

        self.tokenizer = AutoTokenizer.from_pretrained(
            repoid_or_path, config=self.config, padding_side="left"
        )
        self.tokenizer.pad_token = self.tokenizer.eos_token

        return AutoModelForCausalLM.from_config(self.config, trust_remote_code=True)

    def load_local(self, repoid_or_path, *args, **kwargs) -> PreTrainedModel:
        return AutoModelForCausalLM.from_pretrained(
            repoid_or_path, *args, config=self.config, **kwargs
        )

    def prepare_inputs(
        self,
        inputs: Union[
            str, List[str], List[List[str]], List[int], List[List[int]], torch.Tensor
        ],
        *args,
        **kwargs,
    ) -> BatchEncoding:
        """_summary_

        Args:
            inputs (_type_): _description_

        Returns:
            BatchEncoding: _description_
        """

        if isinstance(inputs, str) or (
            isinstance(inputs, list) and isinstance(inputs[0], int)
        ):
            inputs = [inputs]

        if isinstance(inputs, torch.Tensor) and inputs.ndim == 1:
            inputs = inputs.unsqueeze(0)

        if not isinstance(inputs[0], str):
            inputs = [self.tokenizer.decode(ids) for ids in inputs]

        return self.tokenizer(
            inputs, *args, return_tensors="pt", padding=True, **kwargs
        )

    def run_meta(self, inputs, *args, **kwargs) -> None:
        self.meta_model(*args, **inputs.copy().to("meta"), **kwargs)

        return inputs["input_ids"]

    def run_local(self, inputs, *args, **kwargs) -> None:
        return self.local_model.generate(
            *args, **inputs.to(self.local_model.device), **kwargs
        )
