# Neum AI Tools

Collection of tools made to help implement RAG pipelines. Can be used directly or through Neum AI.

| :exclamation:  This utilities are currently in experimental phase.   |
|----------------------------------------------------------------------|

## Tools

- [Semantic Helpers](./neumai_tools/SemanticHelpers/): LLM based tools to help augment RAG pipelines. Includes generating semantic strategies to generate chunking code, select fields to capture as metadata and as content when leveraging RAG on top of structured data.
- [Interop Helpers](./neumai_tools/InteropHelpers/): Utilities to connect frameworks like Langchain and Llama Index with Neum AI. If there are data connectors that you want to leverage, you can use the utilities to translate interfaces.
- [Pipeline Collection](./neumai_tools/PipelineCollection/): Treat a collection of pipelines as a single entity to perform search and other actions. Allows you to silo data into pipelines with their unique set of transformations, embed model and sink and then bring them back together as a single entity to retrieve data.
- [Dataset Evaluation](./neumai_tools/DatasetEvaluation/): Create datasets of queries and expected outputs that you can run against a given pipeline or pipeline collection. 
