# 知识图谱项目

这是一个关于"知识图谱"主题的知识图谱构建项目，从数据抓取到可视化的完整流程。

## 项目结构

```
knowledge_graph/
├── crawler/        # 爬虫模块，负责数据抓取
├── processor/      # 数据处理模块，负责数据清洗和实体抽取
├── graph_builder/  # 图谱构建模块，负责建立实体和关系
├── storage/        # 存储模块，负责图谱的持久化
├── visualization/  # 可视化模块，负责图谱的展示
└── data/           # 存放数据的目录
```

## 环境配置

1. 创建虚拟环境:
```bash
python -m venv kg_env
```

2. 激活虚拟环境:
- Windows: `kg_env\Scripts\activate`
- Linux/Mac: `source kg_env/bin/activate`

3. 安装依赖:
```bash
pip install -r requirements.txt
```

4. 安装中文语言模型:
```bash
python -m spacy download zh_core_web_sm
```

## 使用方法

1. 数据抓取:
```bash
python -m knowledge_graph.crawler.spider
```

2. 数据处理:
```bash
python -m knowledge_graph.processor.processor
```

3. 图谱构建:
```bash
python -m knowledge_graph.graph_builder.builder
```

4. 图谱存储:
```bash
python -m knowledge_graph.storage.store
```

5. 图谱可视化:
```bash
python -m knowledge_graph.visualization.visualize
```

6. 运行完整流程:
```bash
python main.py
```

## 知识图谱标准

本项目遵循的知识图谱标准：

1. 三元组结构：(主体, 关系, 客体)
2. 使用RDF（资源描述框架）进行表示
3. 采用OWL（Web本体语言）定义本体
4. 使用SPARQL进行查询
5. 使用标准命名空间和URI

## 许可证

MIT 