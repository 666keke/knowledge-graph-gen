# Knowledge Graph Project | [中文](README.md)

This is a complete knowledge graph construction project on the topic of "Knowledge Graph", covering the entire process from data crawling to visualization.

## Key Features

1. **Large Language Model Entity/Relation Extraction**: Utilizes OpenAI API to automatically extract entities and relationships from text, transforming unstructured text into knowledge graphs using advanced language models

2. **Diversified Entity Extraction**:
   - SpaCy named entity recognition
   - Jieba Chinese word segmentation and part-of-speech tagging
   - Regular expression pattern matching
   - Predefined terminology library matching

3. **Multi-strategy Relationship Extraction**:
   - Pattern-based relationship extraction
   - LLM-based relationship extraction
   - Entity co-occurrence analysis

4. **Intelligent Crawler**:
   - Traditional web crawler (supporting Baidu Baike, Wikipedia, CSDN, and other multi-source data)
   - AI agent-driven browser automation crawler capable of autonomous navigation and information extraction

5. **Graph Storage and Query**:
   - Support for RDF triple storage
   - SPARQL query interface
   - Compatibility with mainstream graph databases

6. **Interactive Visualization**: Generate interactive knowledge graph visualization interface with support for zooming, filtering, and exploration

## Project Structure

```
knowledge_graph/
├── crawler/        # Crawler module for data collection
├── processor/      # Data processing module for cleaning and entity extraction
├── graph_builder/  # Graph construction module for establishing entities and relationships
├── storage/        # Storage module for graph persistence
├── visualization/  # Visualization module for graph display
└── data/           # Directory for data storage
```

## Environment Setup

1. Create a virtual environment:
```bash
python -m venv kg_env
```

2. Activate the virtual environment:
- Windows: `kg_env\Scripts\activate`
- Linux/Mac: `source kg_env/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Chinese language model:
```bash
python -m spacy download zh_core_web_sm
```

## Usage

1. Data crawling:
```bash
python -m knowledge_graph.crawler.spider
```

2. Data processing:
```bash
python -m knowledge_graph.processor.processor
```

3. Graph construction:
```bash
python -m knowledge_graph.graph_builder.builder
```

4. Graph storage:
```bash
python -m knowledge_graph.storage.store
```

5. Graph visualization:
```bash
python -m knowledge_graph.visualization.visualize
```

6. Run the complete pipeline:
```bash
python main.py
```

## Knowledge Graph Standards

Standards followed in this project:

1. Triple structure: (subject, relationship, object)
2. Representation using RDF (Resource Description Framework)
3. Ontology definition using OWL (Web Ontology Language)
4. Querying with SPARQL
5. Using standard namespaces and URIs

## License

MIT 