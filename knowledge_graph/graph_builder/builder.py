import os
import json
import logging
import networkx as nx
import rdflib
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KnowledgeGraphBuilder:
    """知识图谱构建器，用于构建和管理知识图谱"""
    
    def __init__(self, input_dir='knowledge_graph/data', output_dir='knowledge_graph/data'):
        """初始化图谱构建器
        
        Args:
            input_dir: 输入数据目录
            output_dir: 输出数据目录
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 初始化NetworkX图
        self.nx_graph = nx.DiGraph()
        
        # 初始化RDF图
        self.rdf_graph = Graph()
        
        # 定义命名空间
        self.kg_ns = Namespace("http://knowledge-graph.org/kg-schema#")
        self.rdf_graph.bind("kg", self.kg_ns)
        self.rdf_graph.bind("rdf", RDF)
        self.rdf_graph.bind("rdfs", RDFS)
        self.rdf_graph.bind("owl", OWL)
        self.rdf_graph.bind("xsd", XSD)
        
    def load_data(self):
        """加载处理后的实体和关系数据"""
        # 加载实体数据
        entities_file = os.path.join(self.input_dir, 'entities.json')
        try:
            with open(entities_file, 'r', encoding='utf-8') as f:
                self.entities = json.load(f)
            logger.info(f"已加载 {len(self.entities)} 个实体")
        except Exception as e:
            logger.error(f"加载实体文件失败: {str(e)}")
            self.entities = []
        
        # 加载关系数据
        relations_file = os.path.join(self.input_dir, 'relations.json')
        try:
            with open(relations_file, 'r', encoding='utf-8') as f:
                self.relations = json.load(f)
            logger.info(f"已加载 {len(self.relations)} 个关系")
        except Exception as e:
            logger.error(f"加载关系文件失败: {str(e)}")
            self.relations = []
            
    def create_networkx_graph(self):
        """使用NetworkX创建图谱"""
        logger.info("开始构建NetworkX图谱...")
        
        # 添加实体作为节点
        for entity in self.entities:
            self.nx_graph.add_node(
                entity['text'],
                label=entity.get('label', ''),
                type=entity.get('type', '')
            )
        
        # 添加关系作为边
        for relation in self.relations:
            subject = relation.get('subject', '')
            predicate = relation.get('predicate', '')
            obj = relation.get('object', '')
            
            if subject and obj:
                self.nx_graph.add_edge(
                    subject,
                    obj,
                    label=predicate,
                    sentence=relation.get('sentence', '')
                )
                
        logger.info(f"NetworkX图谱构建完成，包含 {self.nx_graph.number_of_nodes()} 个节点和 {self.nx_graph.number_of_edges()} 条边")
        
    def create_rdf_graph(self):
        """使用RDFLib创建RDF图谱"""
        logger.info("开始构建RDF图谱...")
        
        # 创建本体类
        self.rdf_graph.add((self.kg_ns.Entity, RDF.type, OWL.Class))
        self.rdf_graph.add((self.kg_ns.KGTerm, RDF.type, OWL.Class))
        self.rdf_graph.add((self.kg_ns.KGTerm, RDFS.subClassOf, self.kg_ns.Entity))
        
        # 创建关系类型
        relation_types = set(relation['predicate'] for relation in self.relations) if self.relations else set()
        for rel_type in relation_types:
            rel_uri = self.kg_ns[rel_type]
            self.rdf_graph.add((rel_uri, RDF.type, OWL.ObjectProperty))
            self.rdf_graph.add((rel_uri, RDFS.domain, self.kg_ns.Entity))
            self.rdf_graph.add((rel_uri, RDFS.range, self.kg_ns.Entity))
        
        # 添加实体
        for entity in self.entities:
            entity_text = entity['text']
            entity_uri = self.kg_ns[self._normalize_uri(entity_text)]
            
            # 添加实体类型
            self.rdf_graph.add((entity_uri, RDF.type, self.kg_ns.Entity))
            
            # 如果是知识图谱术语，添加为KGTerm类
            if entity.get('label') == 'KG_TERM':
                self.rdf_graph.add((entity_uri, RDF.type, self.kg_ns.KGTerm))
            
            # 添加标签
            self.rdf_graph.add((entity_uri, RDFS.label, Literal(entity_text, lang="zh")))
        
        # 添加关系
        for relation in self.relations:
            subj_text = relation.get('subject', '')
            pred_text = relation.get('predicate', '')
            obj_text = relation.get('object', '')
            
            if subj_text and pred_text and obj_text:
                subj_uri = self.kg_ns[self._normalize_uri(subj_text)]
                pred_uri = self.kg_ns[pred_text]
                obj_uri = self.kg_ns[self._normalize_uri(obj_text)]
                
                # 添加三元组
                self.rdf_graph.add((subj_uri, pred_uri, obj_uri))
        
        logger.info(f"RDF图谱构建完成，包含 {len(self.rdf_graph)} 个三元组")
    
    def _normalize_uri(self, text):
        """将文本规范化为适合URI的形式
        
        Args:
            text: 输入文本
        
        Returns:
            规范化后的URI字符串
        """
        # 移除空格和特殊字符
        uri = text.replace(' ', '_')
        uri = ''.join(c for c in uri if c.isalnum() or c == '_')
        return uri
    
    def save_networkx_graph(self):
        """保存NetworkX图谱"""
        # 保存为GEXF格式（可用于Gephi等工具）
        nx_file = os.path.join(self.output_dir, 'knowledge_graph.gexf')
        nx.write_gexf(self.nx_graph, nx_file)
        logger.info(f"NetworkX图谱已保存为GEXF格式: {nx_file}")
        
        # 保存为GraphML格式
        graphml_file = os.path.join(self.output_dir, 'knowledge_graph.graphml')
        nx.write_graphml(self.nx_graph, graphml_file)
        logger.info(f"NetworkX图谱已保存为GraphML格式: {graphml_file}")
    
    def save_rdf_graph(self):
        """保存RDF图谱"""
        # 保存为Turtle格式
        ttl_file = os.path.join(self.output_dir, 'knowledge_graph.ttl')
        self.rdf_graph.serialize(destination=ttl_file, format='turtle')
        logger.info(f"RDF图谱已保存为Turtle格式: {ttl_file}")
        
        # 保存为N-Triples格式
        nt_file = os.path.join(self.output_dir, 'knowledge_graph.nt')
        self.rdf_graph.serialize(destination=nt_file, format='nt')
        logger.info(f"RDF图谱已保存为N-Triples格式: {nt_file}")
        
        # 保存为RDF/XML格式
        xml_file = os.path.join(self.output_dir, 'knowledge_graph.rdf')
        self.rdf_graph.serialize(destination=xml_file, format='xml')
        logger.info(f"RDF图谱已保存为RDF/XML格式: {xml_file}")
    
    def get_statistics(self):
        """获取图谱统计信息
        
        Returns:
            统计信息字典
        """
        # NetworkX图统计
        nx_stats = {
            'nodes_count': self.nx_graph.number_of_nodes(),
            'edges_count': self.nx_graph.number_of_edges(),
            'density': nx.density(self.nx_graph),
            'is_directed': nx.is_directed(self.nx_graph),
            'top_degree_centrality': sorted(nx.degree_centrality(self.nx_graph).items(), 
                                           key=lambda x: x[1], reverse=True)[:10]
        }
        
        # RDF图统计
        rdf_stats = {
            'triples_count': len(self.rdf_graph),
            'subjects_count': len(set(self.rdf_graph.subjects())),
            'predicates_count': len(set(self.rdf_graph.predicates())),
            'objects_count': len(set(self.rdf_graph.objects()))
        }
        
        return {
            'networkx': nx_stats,
            'rdf': rdf_stats
        }
    
    def save_statistics(self, stats):
        """保存统计信息
        
        Args:
            stats: 统计信息字典
        """
        stats_file = os.path.join(self.output_dir, 'graph_statistics.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        logger.info(f"图谱统计信息已保存到: {stats_file}")
    
    def run(self):
        """运行图谱构建器的完整流程"""
        # 加载数据
        self.load_data()
        
        if not self.entities:
            logger.error("没有找到实体数据，无法构建图谱")
            return
        
        # 构建图谱
        self.create_networkx_graph()
        self.create_rdf_graph()
        
        # 保存图谱
        self.save_networkx_graph()
        self.save_rdf_graph()
        
        # 保存统计信息
        stats = self.get_statistics()
        self.save_statistics(stats)
        
        logger.info("知识图谱构建完成！")

def main():
    """主函数"""
    builder = KnowledgeGraphBuilder()
    builder.run()

if __name__ == "__main__":
    main() 