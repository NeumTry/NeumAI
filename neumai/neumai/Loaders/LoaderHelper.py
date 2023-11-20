from neumai.Loaders import (
    AutoLoader,
    MarkdownLoader,
    JSONLoader,
    CSVLoader,
    PDFLoader,
    HTMLLoader,
)
from neumai.Loaders.LoaderEnum import LoaderEnum
from neumai.Shared.Selector import Selector

def as_loader(dct:dict):
    if dct == None:
        return AutoLoader()
    loader_name = str(dct.get("loader_name", None)).replace(" ","").lower()
    loader_information = dct.get("loader_information", None)
    selector = Selector.as_selector(dct.get("selector", None))
    if loader_name == LoaderEnum.autoloader:
        return AutoLoader(loader_information=loader_information, selector=selector)
    elif loader_name == LoaderEnum.htmlloader:
        return HTMLLoader(loader_information=loader_information, selector=selector)
    elif loader_name == LoaderEnum.markdownloader:
        return MarkdownLoader(loader_information=loader_information, selector=selector)
    elif loader_name == LoaderEnum.JSONLoader:
        return JSONLoader(loader_information=loader_information, selector=selector)
    elif loader_name == LoaderEnum.CSVLoader:
        return CSVLoader(loader_information=loader_information, selector=selector)
    elif loader_name == LoaderEnum.pdfloader:
        return PDFLoader(loader_information=loader_information, selector=selector)
    else: 
        return AutoLoader(loader_information=loader_information, selector=selector)