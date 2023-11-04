<h1 align="center">Neum AI</h1>

<div align="center">
  
  [Homepage](https://www.neum.ai) | [Documentation](https://docs.neum.ai) | [Discord](https://discord.gg/mJeNZYRz4m) | [Twitter](https://twitter.com/neum_ai)
  
  <a href="https://www.ycombinator.com/companies/neum-ai"><img src="https://badgen.net/badge/Y%20Combinator/S23/orange"/></a>
</div>

**[Neum AI](https://neum.ai) is a data platform that helps developers leverage their data to contextualize Large Language Models through Retrieval Augmented Generation (RAG)** This includes
extracting data from existing data sources like document storage and NoSQL, processing the contents into vector embeddings and ingesting the vector embeddings into vector databases for similarity search. 

It provides you a comprehensive solution for RAG that can scale with your application and reduce the time spent integrating services like data connectors, embedding models and vector databases.

## Features

- 🏭 **High throughput distrubted architecture** to handle billions of data points. Allows high degrees of parallelization to optimize embedding generation and ingestion.
- 🧱 **Built-in data connectors** to common data sources, embedding services and vector stores.
- 🔄 **Real-time synchronization** of data sources to ensure your data is always up-to-date. 
- 🤝 **Cohesive data management** to support hybrid retrieval with metdata. Neum AI automatically augments and tracks metadata to provide rich retrieval experience.

## Getting Started

### Neum AI Cloud

Sign up today at [dasboard.neum.ai](https://dashboard.neum.ai). See our [quickstart]() to get started.

### Self-Host

Install the `neumai` package:

```bash
pip install neumai
```

To create your first data pipelines visit our [quickstart]().

## Roadmap

Connectors
- [ ]  MySQL - Source
- [ ]  GitHub - Source
- [ ]  Google Drive - Source
- [ ]  Hugging Face - Embedding
- [ ]  LanceDB - Sink
- [ ]  Milvus - Sink
- [ ]  Chroma - Sink

Search
- [ ]  Retrieval feedback
- [ ]  Filter support
- [ ]  Unified Neum AI filters

Extensibility
- [ ]  Langchain / Llama Index Document to Neum Document converter
- [ ]  Custom chunking and loading

Experimental
- [ ]  Async metadata augmentation
- [ ]  Chat history connector
- [ ]  Structured (SQL and GraphQL) search connector

In this repository, we have included tools that the Neum AI team has built to help in process of ingesting and processing data.

- [neumai-tools](https://pypi.org/project/neumai-tools/): contains pre-processing tools for loading and chunking data before generating vector embeddings.
