<h1 align="center">Neum AI</h1>

<div align="center">
  
  [Homepage](https://www.neum.ai) | [Documentation](https://docs.neum.ai) | [Discord](https://discord.gg/mJeNZYRz4m) | [Twitter](https://twitter.com/neum_ai)
  
  <a href="https://www.ycombinator.com/companies/neum-ai"><img src="https://badgen.net/badge/Y%20Combinator/S23/orange"/></a>
</div>

Core library with Neum AI components to connect, load, chunk and sink vector embeddings. **[Neum AI](https://neum.ai) is a data platform that helps developers leverage their data to contextualize Large Language Models through Retrieval Augmented Generation (RAG)** This includes
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

The Neum AI Cloud supports a large-scale, distrubted architecture to run millions of documents through vector embedding. For the full set of features see: [Cloud vs Local](https://neumai.mintlify.app/get-started/cloud-vs-local)

### Local Development

Install the [`neumai`](https://pypi.org/project/neumai/) package:

```bash
pip install neumai
```

To create your first data pipelines visit our [quickstart]().

### Self-host

If you are interested in deploying Neum AI to your own cloud contact us at [founders@tryneum.com](mailto:founders@tryneum.com).

We will publish soon an open-source self-host that leverages the framework's architecture to do high throughput data processing.

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
- [ ]  Self-Query Retrieval (w/ Metadata attributes generation)

Extensibility
- [ ]  Langchain / Llama Index Document to Neum Document converter
- [ ]  Custom chunking and loading

Experimental
- [ ]  Async metadata augmentation
- [ ]  Chat history connector
- [ ]  Structured (SQL and GraphQL) search connector