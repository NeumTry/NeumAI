import openai
from langchain.docstore.document import Document
from typing import (
    List,
)

def semantic_chunking_strategy(text:str) -> str:
    messages = []
    messages = [
        {"role": "system", "content": ('You are helpful assistant' + 
                                       'Based on a given piece of text provided, describe the correct strategy to split the text.' + 
                                       'Describe the schema you would follow to chunk the text' +
                                       'Be concise, but specific the process to allow a developer to implement it' +
                                       'The goal is for the chunks to mantain the semantic meaning of the text' +
                                       'For example, if I have a text that have several questions and answers, they should be kept together inside the same chunk' +
                                       'If I have a text that has many parapraphs, ideally try to keep pargraphs within the same chunk' +
                                       'Same applies for sentences, try to keep them together within the same chunk and not cut in the middle.')},
        {"role": "user", "content": text}
    ]
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=messages,
        temperature=0.9
        
    )
    response_message = response.choices[0].message
    return response_message

def semantic_chunking_strategy_code(text:str, chunking_strategy:str) -> str:
    messages = []
    messages = [
        {"role": "system", "content": ('You are helpful developer that writes python code.' + 
                                        'Output the code in this format: ```python def split_text_into_chunks(text): <Insert Code>```' +
                                        'The function `split_text_into_chunks` should output an array of chunks.'
                                        'Implement the strategy provided by the user to help split text.')},
        {"role": "user", "content": chunking_strategy}
    ]
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=messages,
        temperature=0.9
        
    )
    response_message = response.choices[0].message
    return response_message

def semantic_chunking_code(text:str) -> str:
    fixed_text = cut_text(text)
    chunking_strategy = semantic_chunking_strategy(text=fixed_text)['content']
    chunking_code = semantic_chunking_strategy_code(text=fixed_text, chunking_strategy=chunking_strategy)['content']
    chunking_code_exec = chunking_code.split("```python")[1].split("```")[0]
    return chunking_code_exec

def semantic_chunking(documents:List[Document], chunking_code_exec: str) -> List[Document]:
    exec(chunking_code_exec, globals())
    result_doc = []
    for doc in documents:
        results = split_text_into_chunks(doc.page_content)
        for result in results:
            result_doc.append(Document(page_content=result, metadata=doc.metadata))
    return result_doc


def cut_text(s):
    words = s.split()  # Split the string into a list of words
    word_count = len(words)
    
    if word_count <= 750:
        return s  # If the string is less than or equal to 750 words, return the entire string
    
    if word_count > 750:
        if word_count >= 1250:  # Check if we can skip 500 and still get 750
            return ' '.join(words[500:1250])  # Skip the first 500 words and take the next 750 words
        else:
            return ' '.join(words[word_count - 750:word_count])  # Take the last 750 words
