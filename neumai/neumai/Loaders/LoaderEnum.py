from enum import Enum

class LoaderEnum(str, Enum):
    autoloader = "autoloader"
    htmlloader = "htmlloader"
    markdownloader = "markdownloader"
    csvloader = "csvloader"
    jsonloader = "jsonloader"
    pdfloader = "pdfloader"

    def as_loader_enum(loader_name: str):
        if loader_name == None or loader_name == "":
            return None
        try:
            enum_to_return = LoaderEnum[loader_name.lower()]
            return enum_to_return
        except KeyError as e:
            return None