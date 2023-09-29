import os

import yaml

from .modeling.Config import ConfigModel
from .patching import *

PATH = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(PATH, "config.yaml"), "r") as file:
    CONFIG = ConfigModel(**yaml.safe_load(file))

from .models.DiffuserModel import DiffuserModel
from .models.LanguageModel import LanguageModel
