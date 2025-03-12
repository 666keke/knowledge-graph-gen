import os
import json
import logging
import sqlite3
import rdflib
from rdflib import Graph
import pickle
import networkx as nx

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KnowledgeGraphStorage:
    """知识图谱存储类，用于持久化存储知识图谱"""
    
    def __init__(self, input_dir='knowledge_graph/data', output_dir='knowledge_graph/data'):
        """初始化存储类
        
        Args:
            input_dir: 输入数据目录
            output_dir: 输出数据目录
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
    def load_networkx_graph(self):
        """加载NetworkX图谱
        
        Returns:
            加载的NetworkX图谱
        """
        graphml_file = os.path.join(self.input_dir, 'knowledge_graph.graphml')
        
        try:
            nx_graph = nx.read_graphml(graphml_file)
            logger.info(f"已从 {graphml_file} 加载NetworkX图谱")
            return nx_graph
        except Exception as e:
            logger.error(f"加载NetworkX图谱失败: {str(e)}")
            return None
    
    def load_rdf_graph(self):
        """加载RDF图谱
        
        Returns:
            加载的RDF图谱
        """
        ttl_file = os.path.join(self.input_dir, 'knowledge_graph.ttl')
        
        try:
            rdf_graph = Graph()
            rdf_graph.parse(ttl_file, format='turtle')
            logger.info(f"已从 {ttl_file} 加载RDF图谱")
            return rdf_graph
        except Exception as e:
            logger.error(f"加载RDF图谱失败: {str(e)}")
            return None
    
    def store_as_sqlite(self, nx_graph):
        """将NetworkX图谱存储为SQLite数据库
        
        Args:
            nx_graph: NetworkX图谱
        """
        if not nx_graph:
            logger.error("没有可用的NetworkX图谱，无法存储为SQLite")
            return
            
        db_file = os.path.join(self.output_dir, 'knowledge_graph.db')
        
        try:
            # 连接到SQLite数据库（如果不存在则创建）
            conn = sqlite3.connect(db_file)
            cursor = conn.cursor()
            
            # 创建节点表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS nodes (
                id TEXT PRIMARY KEY,
                label TEXT,
                type TEXT
            )
            ''')
            
            # 创建边表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT,
                target TEXT,
                label TEXT,
                sentence TEXT,
                FOREIGN KEY (source) REFERENCES nodes (id),
                FOREIGN KEY (target) REFERENCES nodes (id)
            )
            ''')
            
            # 插入节点数据
            for node, attrs in nx_graph.nodes(data=True):
                cursor.execute('INSERT OR REPLACE INTO nodes VALUES (?, ?, ?)',
                              (str(node), attrs.get('label', ''), attrs.get('type', '')))
            
            # 插入边数据
            for source, target, attrs in nx_graph.edges(data=True):
                cursor.execute('INSERT INTO edges (source, target, label, sentence) VALUES (?, ?, ?, ?)',
                              (str(source), str(target), attrs.get('label', ''), attrs.get('sentence', '')))
            
            # 提交事务
            conn.commit()
            logger.info(f"图谱已成功存储为SQLite数据库: {db_file}")
            
            # 关闭连接
            conn.close()
            
        except Exception as e:
            logger.error(f"存储为SQLite数据库失败: {str(e)}")
    
    def store_as_pickle(self, nx_graph):
        """将NetworkX图谱存储为pickle文件
        
        Args:
            nx_graph: NetworkX图谱
        """
        if not nx_graph:
            logger.error("没有可用的NetworkX图谱，无法存储为pickle")
            return
            
        pickle_file = os.path.join(self.output_dir, 'knowledge_graph.pkl')
        
        try:
            with open(pickle_file, 'wb') as f:
                pickle.dump(nx_graph, f)
            logger.info(f"图谱已成功存储为pickle文件: {pickle_file}")
        except Exception as e:
            logger.error(f"存储为pickle文件失败: {str(e)}")
    
    def store_as_json(self, nx_graph):
        """将NetworkX图谱存储为JSON格式
        
        Args:
            nx_graph: NetworkX图谱
        """
        if not nx_graph:
            logger.error("没有可用的NetworkX图谱，无法存储为JSON")
            return
            
        json_file = os.path.join(self.output_dir, 'knowledge_graph.json')
        
        try:
            # 准备节点数据
            nodes = []
            for node, attrs in nx_graph.nodes(data=True):
                nodes.append({
                    'id': str(node),
                    'label': attrs.get('label', ''),
                    'type': attrs.get('type', '')
                })
            
            # 准备边数据
            edges = []
            for source, target, attrs in nx_graph.edges(data=True):
                edges.append({
                    'source': str(source),
                    'target': str(target),
                    'label': attrs.get('label', ''),
                    'sentence': attrs.get('sentence', '')
                })
            
            # 组合为一个完整的图结构
            graph_data = {
                'nodes': nodes,
                'edges': edges
            }
            
            # 写入JSON文件
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"图谱已成功存储为JSON文件: {json_file}")
        except Exception as e:
            logger.error(f"存储为JSON文件失败: {str(e)}")
    
    def create_sparql_endpoints(self, rdf_graph):
        """创建SPARQL查询示例
        
        Args:
            rdf_graph: RDF图谱
        """
        if not rdf_graph:
            logger.error("没有可用的RDF图谱，无法创建SPARQL示例")
            return
            
        sparql_examples_file = os.path.join(self.output_dir, 'sparql_examples.txt')
        
        try:
            with open(sparql_examples_file, 'w', encoding='utf-8') as f:
                # 写入一些示例SPARQL查询
                f.write("# SPARQL查询示例\n\n")
                
                # 示例1：查询所有的类
                f.write("# 示例1：查询所有的类\n")
                f.write("""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT ?class
WHERE {
    ?class rdf:type owl:Class .
}
                """)
                f.write("\n\n")
                
                # 示例2：查询所有的知识图谱术语
                f.write("# 示例2：查询所有的知识图谱术语\n")
                f.write("""
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX kg: <http://knowledge-graph.org/kg-schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?term ?label
WHERE {
    ?term rdf:type kg:KGTerm .
    ?term rdfs:label ?label .
}
                """)
                f.write("\n\n")
                
                # 示例3：查询所有的"is_a"关系
                f.write('# 示例3：查询所有的"is_a"关系\n')
                f.write("""
PREFIX kg: <http://knowledge-graph.org/kg-schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?subject ?object
WHERE {
    ?subject kg:is_a ?object .
}
                """)
                f.write("\n\n")
                
                # 示例4：查询含有特定实体的三元组
                f.write('# 示例4：查询含有"知识图谱"实体的三元组\n')
                f.write("""
PREFIX kg: <http://knowledge-graph.org/kg-schema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?predicate ?object ?objectLabel
WHERE {
    ?subject rdfs:label "知识图谱"@zh .
    ?subject ?predicate ?object .
    ?object rdfs:label ?objectLabel .
}
                """)
                
            logger.info(f"SPARQL查询示例已保存到: {sparql_examples_file}")
        except Exception as e:
            logger.error(f"创建SPARQL示例失败: {str(e)}")
    
    def run(self):
        """运行存储流程"""
        # 加载图谱
        nx_graph = self.load_networkx_graph()
        rdf_graph = self.load_rdf_graph()
        
        if not nx_graph and not rdf_graph:
            logger.error("没有找到可用的图谱数据")
            return
        
        # 存储为不同格式
        if nx_graph:
            self.store_as_sqlite(nx_graph)
            self.store_as_pickle(nx_graph)
            self.store_as_json(nx_graph)
        
        if rdf_graph:
            self.create_sparql_endpoints(rdf_graph)
        
        logger.info("知识图谱存储完成！")

def main():
    """主函数"""
    storage = KnowledgeGraphStorage()
    storage.run()

if __name__ == "__main__":
    main() 