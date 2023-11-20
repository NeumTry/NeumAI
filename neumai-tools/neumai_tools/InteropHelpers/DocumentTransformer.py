from langchain.docstore.document import Document as LangChainDocument
from llama_index import Document as LlamaIndexDocument
from neumai.Shared.NeumDocument import NeumDocument
from uuid import uuid4

def document_transformer_langchain(document:LangChainDocument, id:str = uuid4()):
    return NeumDocument(
        id=id,
        content=document.page_content,
        metadata=document.metadata
    )

def document_transformer_llamaIndex(document:LlamaIndexDocument):
    return NeumDocument(
        id=document.doc_id,
        content=document.text,
        metadata=document.metadata
    )