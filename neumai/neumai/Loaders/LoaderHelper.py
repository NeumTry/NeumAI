from neumai.Loaders import (
    AutoLoader,
    LoaderEnum,
    MarkdownLoader,
    NeumJSONLoader,
    NeumCSVLoader,
    PDFLoader,
    HTMLLoader,
)
from neumai.Shared.Selector import Selector

def as_loader(dct:dict):
    if dct == None:
        return AutoLoader()
    loader_name = dct.get("loader_name", None)
    loader_information = dct.get("loader_information", None)
    selector = Selector.as_selector(dct.get("selector", None))
    if loader_name == LoaderEnum.autoloader:
        return AutoLoader(loader_information=loader_information, selector=selector)
    elif loader_name == LoaderEnum.htmlloader:
        return HTMLLoader(loader_information=loader_information, selector=selector)
    elif loader_name == LoaderEnum.markdownloader:
        return MarkdownLoader(loader_information=loader_information, selector=selector)
    elif loader_name == LoaderEnum.neumjsonloader:
        return NeumJSONLoader(loader_information=loader_information, selector=selector)
    elif loader_name == LoaderEnum.neumcsvloader:
        return NeumCSVLoader(loader_information=loader_information, selector=selector)
    elif loader_name == LoaderEnum.pdfloader:
        return PDFLoader(loader_information=loader_information, selector=selector)
    else: 
        return AutoLoader(loader_information=loader_information, selector=selector)