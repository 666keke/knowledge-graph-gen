#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import logging
import json
from knowledge_graph.crawler.spider import KnowledgeGraphCrawler
from knowledge_graph.processor.processor import KnowledgeProcessor
from knowledge_graph.visualization.visualize import KnowledgeGraphVisualizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_crawler():
    """测试爬虫优化"""
    logger.info("开始测试爬虫优化...")
    
    # 创建测试目录
    test_dir = "test_data"
    if not os.path.exists(test_dir):
        os.makedirs(test_dir)
    
    # 初始化爬虫
    crawler = KnowledgeGraphCrawler(output_dir=test_dir)
    
    # 测试百度百科爬取
    baidu_data = crawler.crawl_baidu_baike(keyword='知识图谱', max_pages=2)
    crawler.save_data(baidu_data, 'test_baidu_kg_data.json')
    
    # 测试维基百科爬取
    try:
        wiki_data = crawler.crawl_wikipedia(keyword='知识图谱', max_pages=1)
        crawler.save_data(wiki_data, 'test_wiki_kg_data.json')
    except Exception as e:
        logger.error(f"维基百科爬取测试失败: {str(e)}")
    
    # 测试CSDN博客爬取
    try:
        csdn_data = crawler.crawl_csdn_blogs(keyword='知识图谱', max_pages=1)
        crawler.save_data(csdn_data, 'test_csdn_kg_data.json')
    except Exception as e:
        logger.error(f"CSDN博客爬取测试失败: {str(e)}")
    
    logger.info("爬虫测试完成")

def test_processor():
    """测试处理器优化"""
    logger.info("开始测试处理器优化...")
    
    # 测试目录
    test_dir = "test_data"
    
    # 初始化处理器
    processor = KnowledgeProcessor(input_dir=test_dir, output_dir=test_dir)
    
    # 测试实体提取
    test_text = """
    知识图谱是一种结构化的语义知识库，用于描述物理世界中的概念实体及其相互关系。
    它由本体论、实体和关系组成。知识图谱技术包括知识表示、知识抽取、知识融合和知识推理等。
    RDF是知识图谱的一种表示方式，SPARQL是查询RDF的语言。
    """
    
    entities = processor.extract_entities(test_text)
    logger.info(f"提取到 {len(entities)} 个实体")
    
    # 测试关系提取
    relations = processor.extract_relations(test_text, entities)
    logger.info(f"提取到 {len(relations)} 个关系")
    
    # 保存测试结果
    with open(os.path.join(test_dir, 'test_entities.json'), 'w', encoding='utf-8') as f:
        json.dump(entities, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(test_dir, 'test_relations.json'), 'w', encoding='utf-8') as f:
        json.dump(relations, f, ensure_ascii=False, indent=2)
    
    logger.info("处理器测试完成")

def test_visualization():
    """测试可视化优化"""
    logger.info("开始测试可视化优化...")
    
    # 测试目录
    test_dir = "test_data"
    
    # 创建一个简单的测试图谱
    import networkx as nx
    
    G = nx.DiGraph()
    
    # 添加节点
    G.add_node("知识图谱", label="知识图谱", type="TERM")
    G.add_node("本体论", label="本体论", type="TERM")
    G.add_node("RDF", label="RDF", type="TERM")
    G.add_node("SPARQL", label="SPARQL", type="TERM")
    G.add_node("知识表示", label="知识表示", type="TERM")
    
    # 添加边
    G.add_edge("知识图谱", "本体论", label="includes", sentence="知识图谱包括本体论")
    G.add_edge("知识图谱", "RDF", label="uses", sentence="知识图谱使用RDF")
    G.add_edge("RDF", "SPARQL", label="queried_by", sentence="RDF通过SPARQL查询")
    G.add_edge("知识图谱", "知识表示", label="requires", sentence="知识图谱需要知识表示")
    
    # 保存图谱
    nx.write_graphml(G, os.path.join(test_dir, 'knowledge_graph.graphml'))
    
    # 创建测试统计数据
    stats = {
        "networkx": {
            "nodes_count": len(G.nodes),
            "edges_count": len(G.edges),
            "top_degree_centrality": [
                ["知识图谱", 0.75],
                ["RDF", 0.5],
                ["本体论", 0.25],
                ["SPARQL", 0.25],
                ["知识表示", 0.25]
            ]
        },
        "rdf": {
            "triples_count": len(G.edges)
        }
    }
    
    with open(os.path.join(test_dir, 'graph_statistics.json'), 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    
    # 初始化可视化器
    visualizer = KnowledgeGraphVisualizer(input_dir=test_dir, output_dir=test_dir)
    
    # 测试可视化
    visualizer.run()
    
    logger.info("可视化测试完成")

def main():
    """主函数"""
    # 测试爬虫
    test_crawler()
    
    # 测试处理器
    test_processor()
    
    # 测试可视化
    test_visualization()
    
    logger.info("所有测试完成")

if __name__ == "__main__":
    main()