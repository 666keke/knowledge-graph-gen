# 知识图谱项目 | [English](README_EN.md)

这是一个关于"知识图谱"主题的知识图谱构建项目，从数据抓取到可视化的完整流程。

## 特色功能

1. **大模型实体/关系抽取**：利用OpenAI API自动从文本中提取实体和关系，通过先进的语言模型将非结构化文本转换为知识图谱

2. **多元化实体抽取**：
   - SpaCy命名实体识别
   - Jieba中文分词与词性标注
   - 正则表达式模式匹配
   - 预定义术语库匹配

3. **多策略关系抽取**：
   - 基于模式匹配的关系抽取
   - 基于大模型的关系抽取
   - 实体共现分析

4. **智能爬虫**：
   - 传统网页爬虫（支持百度百科、维基百科、CSDN等多源数据）
   - AI代理驱动的浏览器自动化爬虫，能够自主导航和提取信息

5. **图谱存储与查询**：
   - 支持RDF三元组存储
   - 提供SPARQL查询接口
   - 兼容主流图数据库

6. **交互式可视化**：生成交互式知识图谱可视化界面，支持缩放、筛选和探索

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