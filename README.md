<h1 align="center">Neum AI</h1>

<div align="center">
  
  [Homepage](https://www.neum.ai) | [Documentation](https://docs.neum.ai) | [Blog](https://neum.ai/blog) | [Discord](https://discord.gg/mJeNZYRz4m) | [Twitter](https://twitter.com/neum_ai)
  
  <a href="https://www.ycombinator.com/companies/neum-ai"><img src="https://badgen.net/badge/Y%20Combinator/S23/orange"/></a> 
  <a href="https://pypi.org/project/neumai/">
    <img src="https://img.shields.io/pypi/v/neumai" alt="PyPI">
  </a>
</div>

![Neum AI Hero](https://uploads-ssl.webflow.com/6552c062a6c96c60086c77df/6557cfde1ff0648321e5d3ba_Group%2066.png)

**[Neum AI](https://neum.ai) is a data platform that helps developers leverage their data to contextualize Large Language Models through Retrieval Augmented Generation (RAG)** This includes
extracting data from existing data sources like document storage and NoSQL, processing the contents into vector embeddings and ingesting the vector embeddings into vector databases for similarity search. 

It provides you a comprehensive solution for RAG that can scale with your application and reduce the time spent integrating services like data connectors, embedding models and vector databases.

## Features

- 🏭 **High throughput distributed architecture** to handle billions of data points. Allows high degrees of parallelization to optimize embedding generation and ingestion.
- 🧱 **Built-in data connectors** to common data sources, embedding services and vector stores.
- 🔄 **Real-time synchronization** of data sources to ensure your data is always up-to-date. 
- ♻ **Customizable data pre-processing** in the form of loading, chunking and selecting.
- 🤝 **Cohesive data management** to support hybrid retrieval with metadata. Neum AI automatically augments and tracks metadata to provide rich retrieval experience.

## Getting Started

### Neum AI Cloud

Sign up today at [dashboard.neum.ai](https://dashboard.neum.ai). See our [quickstart](https://docs.neum.ai/get-started/quickstart) to get started.

The Neum AI Cloud supports a large-scale, distributed architecture to run millions of documents through vector embedding. For the full set of features see: [Cloud vs Local](https://neumai.mintlify.app/get-started/cloud-vs-local)

### Local Development

Install the [`neumai`](https://pypi.org/project/neumai/) package:

```bash
pip install neumai
```

To create your first data pipelines visit our [quickstart](https://docs.neum.ai/get-started/quickstart).

At a high level, a pipeline consists of one or multiple sources to pull data from, one embed connector to vectorize the content, and one sink connector to store said vectors.
With this snippet of code we will craft all of these and run a pipeline:
<details open>
  <summary>Open snippet</summary>
  
  ```python
  
    from neumai.DataConnectors.WebsiteConnector import WebsiteConnector
    from neumai.Shared.Selector import Selector
    from neumai.Loaders.HTMLLoader import HTMLLoader
    from neumai.Chunkers.RecursiveChunker import RecursiveChunker
    from neumai.Sources.SourceConnector import SourceConnector
    from neumai.EmbedConnectors import OpenAIEmbed
    from neumai.SinkConnectors import WeaviateSink
    from neumai.Pipelines import Pipeline

    website_connector =  WebsiteConnector(
        url = "https://www.neum.ai/post/retrieval-augmented-generation-at-scale",
        selector = Selector(
            to_metadata=['url']
        )
    )
    source = SourceConnector(
      data_connector = website_connector, 
      loader = HTMLLoader(), 
      chunker = RecursiveChunker()
    )
  
    openai_embed = OpenAIEmbed(
      api_key = "<OPEN AI KEY>",
    )
  
    weaviate_sink = WeaviateSink(
      url = "your-weaviate-url",
      api_key = "your-api-key",
      class_name = "your-class-name",
    )
  
    pipeline = Pipeline(
      sources=[source], 
      embed=openai_embed, 
      sink=weaviate_sink
    )
    pipeline.run()
  
    results = pipeline.search(
      query="What are the challenges with scaling RAG?", 
      number_of_results=3
    )
  
    for result in results:
      print(result.metadata)
  ```
</details>

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

Additional tooling for Neum AI can be found here:

- [neumai-tools](https://pypi.org/project/neumai-tools/): contains pre-processing tools for loading and chunking data before generating vector embeddings.
