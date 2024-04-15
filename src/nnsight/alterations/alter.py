from .PropertyEdit import PropertyEdit
from .Editor import Editor
from ..envoy import Envoy
from ..models.NNsightModel import NNsight


def alter(
        model: NNsight, 
        name_alterations: dict = {},
        property_alterations: dict = {},
    ):

    # Clear existing _editor if it exists
    if hasattr(model, "_editor"):
        restore(model)

    # Wrap module in new Envoy class
    if name_alterations:
        model._envoy = Envoy(model._model, attr_map=name_alterations)

    if property_alterations:
        editor = Editor(model._envoy, property_alterations)
        model._editor = editor
        model._editor.__enter__()

def restore(model):
    model._editor.__exit__(None, None, None)

    model._envoy = Envoy(model._model)