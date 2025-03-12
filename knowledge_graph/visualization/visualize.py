import os
import json
import logging
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from pyvis.network import Network
import pandas as pd
import matplotlib as mpl

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 配置matplotlib使用系统默认字体，而不是特定的SimHei字体
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'Microsoft YaHei', 'SimHei', 'sans-serif']
plt.rcParams['axes.unicode_minus'] = False  # 正确显示负号
# 设置全局字体属性
mpl.rcParams['font.family'] = 'sans-serif'
mpl.rcParams['font.size'] = 12

class KnowledgeGraphVisualizer:
    """知识图谱可视化类，用于将知识图谱可视化展示"""
    
    def __init__(self, input_dir='knowledge_graph/data', output_dir='knowledge_graph/data'):
        """初始化可视化器
        
        Args:
            input_dir: 输入数据目录
            output_dir: 输出数据目录
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 设置颜色映射
        self.type_colors = {
            'NER': '#3498db',  # 蓝色
            'CHUNK': '#2ecc71',  # 绿色
            'TERM': '#e74c3c'   # 红色
        }
        
        # 设置关系颜色
        self.relation_colors = {
            'is_a': '#9b59b6',  # 紫色
            'includes': '#f39c12',  # 橙色
            'contains': '#f1c40f',  # 黄色
            'belongs_to': '#1abc9c',  # 青绿色
            'composed_of': '#34495e',  # 深蓝色
            'used_for': '#e67e22',  # 橙红色
            'based_on': '#95a5a6',  # 灰色
            'applied_to': '#d35400'  # 棕色
        }
    
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
    
    def load_json_graph(self):
        """从JSON文件加载图谱数据
        
        Returns:
            加载的图谱数据字典
        """
        json_file = os.path.join(self.input_dir, 'knowledge_graph.json')
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                graph_data = json.load(f)
            logger.info(f"已从 {json_file} 加载JSON图谱数据")
            return graph_data
        except Exception as e:
            logger.error(f"加载JSON图谱数据失败: {str(e)}")
            return None
    
    def visualize_with_matplotlib(self, nx_graph):
        """使用Matplotlib可视化图谱
        
        Args:
            nx_graph: NetworkX图谱
        """
        if not nx_graph:
            logger.error("没有可用的NetworkX图谱，无法使用Matplotlib可视化")
            return
            
        plt.figure(figsize=(15, 10))
        
        # 获取节点颜色
        node_colors = []
        for node, attrs in nx_graph.nodes(data=True):
            node_type = attrs.get('type', '')
            node_colors.append(self.type_colors.get(node_type, '#cccccc'))
        
        # 获取边颜色
        edge_colors = []
        for _, _, attrs in nx_graph.edges(data=True):
            edge_label = attrs.get('label', '')
            edge_colors.append(self.relation_colors.get(edge_label, '#999999'))
        
        # 使用spring布局
        pos = nx.spring_layout(nx_graph, k=0.5, iterations=50)
        
        # 绘制节点
        nx.draw_networkx_nodes(nx_graph, pos, node_size=500, node_color=node_colors, alpha=0.8)
        
        # 绘制边
        nx.draw_networkx_edges(nx_graph, pos, width=1.5, edge_color=edge_colors, alpha=0.7, arrows=True, arrowsize=15)
        font_prop = fm.FontProperties(family=mpl.rcParams['font.sans-serif'][0])
    
        # 绘制标签，使用之前配置的字体
        nx.draw_networkx_labels(nx_graph, pos, font_size=10, font_family=font_prop.get_family())
        # # 绘制标签
        # nx.draw_networkx_labels(nx_graph, pos, font_size=10, font_family='SimHei')
        
        # 保存图像
        plt_file = os.path.join(self.output_dir, 'knowledge_graph_matplotlib.png')
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(plt_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"已使用Matplotlib生成图谱可视化: {plt_file}")
    
    def visualize_with_pyvis(self, nx_graph):
        """使用PyVis可视化图谱（交互式）
        
        Args:
            nx_graph: NetworkX图谱
        """
        if not nx_graph:
            logger.error("没有可用的NetworkX图谱，无法使用PyVis可视化")
            return
            
        # 创建PyVis网络
        net = Network(height='800px', width='100%', notebook=False, directed=True)
        
        # 设置网络选项，添加中文支持
        net.set_options("""
        var options = {
          "nodes": {
            "font": {
              "face": "Microsoft YaHei, Arial, sans-serif",
              "size": 14
            }
          },
          "edges": {
            "font": {
              "face": "Microsoft YaHei, Arial, sans-serif",
              "size": 12
            },
            "smooth": {
              "enabled": true,
              "type": "dynamic"
            }
          },
          "physics": {
            "barnesHut": {
              "gravitationalConstant": -80000,
              "centralGravity": 0.3,
              "springLength": 250,
              "springConstant": 0.001,
              "damping": 0.09
            },
            "minVelocity": 0.75
          }
        }
        """)
        
        # 添加节点
        for node, attrs in nx_graph.nodes(data=True):
            node_type = attrs.get('type', '')
            node_label = attrs.get('label', '')
            
            # 设置节点颜色和标题
            color = self.type_colors.get(node_type, '#cccccc')
            title = f"类型: {node_type}<br>标签: {node_label}"
            
            net.add_node(node, label=node, title=title, color=color)
        
        # 添加边
        for source, target, attrs in nx_graph.edges(data=True):
            edge_label = attrs.get('label', '')
            sentence = attrs.get('sentence', '')
            
            # 设置边颜色和标题
            color = self.relation_colors.get(edge_label, '#999999')
            title = f"关系: {edge_label}<br>句子: {sentence}"
            
            net.add_edge(source, target, title=title, label=edge_label, color=color)
        
        # 保存为HTML文件
        html_file = os.path.join(self.output_dir, 'knowledge_graph_interactive.html')
        
        # 自定义HTML模板，确保正确的字符编码
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>知识图谱可视化</title>
    <style>
        body {
            font-family: "Microsoft YaHei", "SimHei", "STHeiti", sans-serif;
        }
        #mynetwork {
            width: 100%;
            height: 800px;
            border: 1px solid lightgray;
        }
    </style>
    {{ head }}
</head>
<body>
    <div id="mynetwork"></div>
    <script type="text/javascript">
        {{ json }}
        {{ config }}
    </script>
</body>
</html>
        """
        
        net.save_graph(html_file)
        
        # 读取生成的HTML文件并修改编码
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 确保HTML文件包含正确的编码声明
        if '<meta charset="utf-8">' not in html_content:
            html_content = html_content.replace('<head>', '<head>\n    <meta charset="utf-8">')
        
        # 写回文件
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"已使用PyVis生成交互式图谱可视化: {html_file}")
    
    def create_statistics_visualization(self):
        """创建统计信息可视化"""
        stats_file = os.path.join(self.input_dir, 'graph_statistics.json')
        
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats = json.load(f)
                
            # 创建节点和边数量的条形图
            plt.figure(figsize=(10, 6))
            
            # 节点和边数量
            counts = [
                stats['networkx']['nodes_count'],
                stats['networkx']['edges_count'],
                stats['rdf']['triples_count']
            ]
            labels = ['节点数量', '边数量', '三元组数量']
            colors = ['#3498db', '#e74c3c', '#2ecc71']
            
            plt.bar(labels, counts, color=colors)
            plt.title('知识图谱统计信息')
            plt.ylabel('数量')
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # 保存图像
            stats_img_file = os.path.join(self.output_dir, 'knowledge_graph_statistics.png')
            plt.tight_layout()
            plt.savefig(stats_img_file, dpi=300)
            plt.close()
            
            logger.info(f"已生成统计信息可视化: {stats_img_file}")
            
            # 创建中心度Top10的条形图
            plt.figure(figsize=(12, 8))
            
            # 提取中心度数据
            centrality_data = stats['networkx']['top_degree_centrality']
            entities = [item[0] for item in centrality_data]
            centrality_values = [item[1] for item in centrality_data]
            
            # 绘制条形图
            plt.barh(entities, centrality_values, color='#9b59b6')
            plt.title('节点中心度 Top 10')
            plt.xlabel('中心度值')
            plt.grid(axis='x', linestyle='--', alpha=0.7)
            
            # 保存图像
            centrality_img_file = os.path.join(self.output_dir, 'knowledge_graph_centrality.png')
            plt.tight_layout()
            plt.savefig(centrality_img_file, dpi=300)
            plt.close()
            
            logger.info(f"已生成中心度可视化: {centrality_img_file}")
            
        except Exception as e:
            logger.error(f"创建统计信息可视化失败: {str(e)}")
    
    def create_relation_distribution(self, nx_graph):
        """创建关系分布可视化
        
        Args:
            nx_graph: NetworkX图谱
        """
        if not nx_graph:
            logger.error("没有可用的NetworkX图谱，无法创建关系分布可视化")
            return
            
        # 统计关系类型分布
        relation_counts = {}
        for _, _, attrs in nx_graph.edges(data=True):
            rel_type = attrs.get('label', 'unknown')
            relation_counts[rel_type] = relation_counts.get(rel_type, 0) + 1
        
        # 创建饼图
        plt.figure(figsize=(10, 8))
        
        labels = list(relation_counts.keys())
        sizes = list(relation_counts.values())
        colors = [self.relation_colors.get(label, '#999999') for label in labels]
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.title('知识图谱关系类型分布')
        
        # 保存图像
        rel_dist_file = os.path.join(self.output_dir, 'knowledge_graph_relation_distribution.png')
        plt.tight_layout()
        plt.savefig(rel_dist_file, dpi=300)
        plt.close()
        
        logger.info(f"已生成关系分布可视化: {rel_dist_file}")
    
    def create_entity_type_distribution(self, nx_graph):
        """创建实体类型分布可视化
        
        Args:
            nx_graph: NetworkX图谱
        """
        if not nx_graph:
            logger.error("没有可用的NetworkX图谱，无法创建实体类型分布可视化")
            return
            
        # 统计实体类型分布
        entity_type_counts = {}
        for _, attrs in nx_graph.nodes(data=True):
            entity_type = attrs.get('type', 'unknown')
            entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
        
        # 创建饼图
        plt.figure(figsize=(10, 8))
        
        labels = list(entity_type_counts.keys())
        sizes = list(entity_type_counts.values())
        colors = [self.type_colors.get(label, '#999999') for label in labels]
        
        plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
        plt.axis('equal')
        plt.title('知识图谱实体类型分布')
        
        # 保存图像
        entity_dist_file = os.path.join(self.output_dir, 'knowledge_graph_entity_distribution.png')
        plt.tight_layout()
        plt.savefig(entity_dist_file, dpi=300)
        plt.close()
        
        logger.info(f"已生成实体类型分布可视化: {entity_dist_file}")
    
    def create_html_report(self):
        """创建HTML报告，汇总所有可视化结果"""
        # 加载统计数据
        stats_file = os.path.join(self.input_dir, 'graph_statistics.json')
        stats_data = {}
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                stats_data = json.load(f)
        except Exception as e:
            logger.error(f"加载统计数据失败: {str(e)}")
            stats_data = {
                "networkx": {"nodes_count": 0, "edges_count": 0},
                "rdf": {"triples_count": 0}
            }
        
        # 获取统计数据
        nodes_count = stats_data.get("networkx", {}).get("nodes_count", 0)
        edges_count = stats_data.get("networkx", {}).get("edges_count", 0)
        triples_count = stats_data.get("rdf", {}).get("triples_count", 0)
        
        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>知识图谱可视化报告</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --primary-color: #4285f4;
            --secondary-color: #34a853;
            --accent-color: #ea4335;
            --text-color: #202124;
            --text-secondary: #5f6368;
            --background-color: #f8f9fa;
            --card-color: #ffffff;
            --border-color: #dadce0;
            --shadow-color: rgba(60, 64, 67, 0.1);
        }}
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-color);
            padding: 0;
            margin: 0;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 0;
        }}
        
        header {{
            background-color: var(--primary-color);
            color: white;
            padding: 2rem 0;
            margin-bottom: 2rem;
            box-shadow: 0 2px 10px var(--shadow-color);
        }}
        
        header .container {{
            padding: 0 2rem;
        }}
        
        h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }}
        
        header p {{
            font-size: 1.2rem;
            opacity: 0.9;
        }}
        
        .dashboard {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            padding: 0 2rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background-color: var(--card-color);
            border-radius: 8px;
            padding: 1.5rem;
            box-shadow: 0 2px 10px var(--shadow-color);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 5px 15px var(--shadow-color);
        }}
        
        .stat-card h3 {{
            font-size: 1.2rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }}
        
        .stat-card .value {{
            font-size: 2.5rem;
            font-weight: 700;
            color: var(--primary-color);
        }}
        
        .section {{
            background-color: var(--card-color);
            border-radius: 8px;
            padding: 2rem;
            margin: 0 2rem 2rem;
            box-shadow: 0 2px 10px var(--shadow-color);
        }}
        
        h2 {{
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
            color: var(--primary-color);
            padding-bottom: 0.5rem;
            border-bottom: 2px solid var(--border-color);
        }}
        
        .image-container {{
            text-align: center;
            margin: 1.5rem 0;
            overflow: hidden;
            border-radius: 8px;
        }}
        
        img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            transition: transform 0.3s ease;
        }}
        
        .image-container:hover img {{
            transform: scale(1.02);
        }}
        
        .interactive-link {{
            display: inline-block;
            text-align: center;
            margin: 1.5rem 0;
            padding: 1rem 2rem;
            background-color: var(--primary-color);
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-weight: 500;
            transition: background-color 0.3s ease, transform 0.3s ease;
        }}
        
        .interactive-link:hover {{
            background-color: #3367d6;
            transform: translateY(-2px);
        }}
        
        p {{
            margin-bottom: 1rem;
            color: var(--text-secondary);
            font-size: 1.1rem;
        }}
        
        footer {{
            text-align: center;
            padding: 2rem;
            background-color: var(--card-color);
            color: var(--text-secondary);
            border-top: 1px solid var(--border-color);
        }}
        
        .chart-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
            gap: 2rem;
            margin: 2rem 0;
        }}
        
        @media (max-width: 768px) {{
            .dashboard {{
                grid-template-columns: 1fr;
            }}
            
            .chart-grid {{
                grid-template-columns: 1fr;
            }}
            
            h1 {{
                font-size: 2rem;
            }}
            
            .section {{
                padding: 1.5rem;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>知识图谱可视化报告</h1>
            <p>基于爬取的数据构建的知识图谱分析与可视化</p>
        </div>
    </header>
    
    <div class="container">
        <div class="dashboard">
            <div class="stat-card">
                <h3>实体数量</h3>
                <div class="value" id="entities-count">{nodes_count}</div>
            </div>
            <div class="stat-card">
                <h3>关系数量</h3>
                <div class="value" id="relations-count">{edges_count}</div>
            </div>
            <div class="stat-card">
                <h3>三元组数量</h3>
                <div class="value" id="triples-count">{triples_count}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>知识图谱概览</h2>
            <div class="image-container">
                <img src="knowledge_graph_matplotlib.png" alt="知识图谱概览">
            </div>
            <p>上图展示了知识图谱的整体结构，不同颜色代表不同类型的实体和关系。节点表示实体，边表示实体间的关系。</p>
        </div>
        
        <div class="section">
            <h2>交互式知识图谱</h2>
            <p>点击下方按钮打开交互式知识图谱，您可以放大、缩小、拖动节点，以及查看详细信息。悬停在节点或边上可以查看更多信息。</p>
            <div style="text-align: center;">
                <a href="knowledge_graph_interactive.html" class="interactive-link" target="_blank">打开交互式知识图谱</a>
            </div>
        </div>
        
        <div class="section">
            <h2>统计分析</h2>
            <div class="chart-grid">
                <div>
                    <div class="image-container">
                        <img src="knowledge_graph_statistics.png" alt="知识图谱统计信息">
                    </div>
                    <p>上图展示了知识图谱的基本统计信息，包括节点数量、边数量和三元组数量。</p>
                </div>
                <div>
                    <div class="image-container">
                        <img src="knowledge_graph_centrality.png" alt="节点中心度分析">
                    </div>
                    <p>上图展示了知识图谱中中心度最高的10个节点，这些节点在图谱中起着关键作用，代表了知识网络中的核心概念。</p>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>分布分析</h2>
            <div class="chart-grid">
                <div>
                    <div class="image-container">
                        <img src="knowledge_graph_relation_distribution.png" alt="关系类型分布">
                    </div>
                    <p>上图展示了知识图谱中不同类型关系的分布情况，反映了实体间的主要关联方式。</p>
                </div>
                <div>
                    <div class="image-container">
                        <img src="knowledge_graph_entity_distribution.png" alt="实体类型分布">
                    </div>
                    <p>上图展示了知识图谱中不同类型实体的分布情况，反映了知识库中的主要概念类别。</p>
                </div>
            </div>
        </div>
    </div>
    
    <footer>
        <p>知识图谱项目 &copy; 2024 | 基于Python、NetworkX和PyVis构建</p>
    </footer>
</body>
</html>
        """
        
        report_file = os.path.join(self.output_dir, 'knowledge_graph_report.html')
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"已生成HTML报告: {report_file}")
        except Exception as e:
            logger.error(f"创建HTML报告失败: {str(e)}")
    
    def run(self):
        """运行可视化流程"""
        # 加载图谱
        nx_graph = self.load_networkx_graph()
        
        if not nx_graph:
            logger.error("没有找到可用的图谱数据，无法进行可视化")
            return
        
        # 使用Matplotlib生成静态可视化
        self.visualize_with_matplotlib(nx_graph)
        
        # 使用PyVis生成交互式可视化
        self.visualize_with_pyvis(nx_graph)
        
        # 创建统计信息可视化
        self.create_statistics_visualization()
        
        # 创建关系分布可视化
        self.create_relation_distribution(nx_graph)
        
        # 创建实体类型分布可视化
        self.create_entity_type_distribution(nx_graph)
        
        # 创建HTML报告
        self.create_html_report()
        
        logger.info("知识图谱可视化完成！")

def main():
    """主函数"""
    visualizer = KnowledgeGraphVisualizer()
    visualizer.run()

if __name__ == "__main__":
    main() 