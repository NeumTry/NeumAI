from neumai.Loaders import (
    AutoLoader,
    MarkdownLoader,
    NeumJSONLoader,
    NeumCSVLoader,
    PDFLoader,
    HTMLLoader,
)
from neumai.Loaders.Loader import Loader
from neumai.Shared.Selector import Selector
from starlette.exceptions import HTTPException

def as_loader(dct:dict):
    if dct == None:
        raise HTTPException(status_code=500, detail="[x001] An error occured on our end, please email kevin@tryneum.com to unblock you!")
    loader_name = dct.get("loader_name", None)
    loader_information = dct.get("loader_information", None)
    selector = Selector.as_selector(dct.get("selector", None))
    if loader_name == "AutoLoader":
        return AutoLoader(loader_information=loader_information, selector=selector)
    elif loader_name == "MarkdownLoader":
        return MarkdownLoader(loader_information=loader_information, selector=selector)
    elif loader_name == "NeumJSONLoader":
        return NeumJSONLoader(loader_information=loader_information, selector=selector)
    elif loader_name == "NeumCSVLoader":
        return NeumCSVLoader(loader_information=loader_information, selector=selector)
    elif loader_name == "PDFLoader":
        return PDFLoader(loader_information=loader_information, selector=selector)
    elif loader_name == "HTMLLoader":
        return HTMLLoader(loader_information=loader_information, selector=selector)
    return None