import os
import logging
import time
from knowledge_graph.crawler.spider import KnowledgeGraphCrawler
from knowledge_graph.processor.processor import KnowledgeProcessor
from knowledge_graph.graph_builder.builder import KnowledgeGraphBuilder
from knowledge_graph.storage.store import KnowledgeGraphStorage
from knowledge_graph.visualization.visualize import KnowledgeGraphVisualizer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("knowledge_graph.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_pipeline():
    """运行完整的知识图谱构建流程"""
    start_time = time.time()
    logger.info("开始运行知识图谱构建流程...")
    
    # 确保数据目录存在
    data_dir = 'knowledge_graph/data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    # # 步骤1: 数据抓取
    # logger.info("步骤1: 开始数据抓取...")
    # crawler = KnowledgeGraphCrawler(use_trad_method=0)
    # crawler.run()
    
    # 步骤2: 数据处理
    logger.info("步骤2: 开始数据处理...")
    processor = KnowledgeProcessor(use_openai=True)
    processor.run()
    
    # 步骤3: 图谱构建
    logger.info("步骤3: 开始图谱构建...")
    builder = KnowledgeGraphBuilder()
    builder.run()
    
    # 步骤4: 图谱存储
    logger.info("步骤4: 开始图谱存储...")
    storage = KnowledgeGraphStorage()
    storage.run()
    
    # 步骤5: 图谱可视化
    logger.info("步骤5: 开始图谱可视化...")
    visualizer = KnowledgeGraphVisualizer()
    visualizer.run()
    
    # 计算总运行时间
    end_time = time.time()
    total_time = end_time - start_time
    logger.info(f"知识图谱构建流程完成！总耗时: {total_time:.2f} 秒")
    
    # 输出结果位置
    logger.info(f"所有结果文件已保存到: {os.path.abspath(data_dir)}")
    logger.info("可视化报告: knowledge_graph/data/knowledge_graph_report.html")

if __name__ == "__main__":
    run_pipeline() 