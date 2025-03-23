import os
import json
import re
import pandas as pd
import spacy
import logging
import jieba
import jieba.posseg as pseg
import openai
import time
from collections import defaultdict
from urllib.parse import quote

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KnowledgeProcessor:
    """知识处理器，用于清洗和处理爬取的数据，并提取实体和关系"""
    
    def __init__(self, input_dir='knowledge_graph/data', output_dir='knowledge_graph/data', use_openai=True):
        """初始化处理器
        
        Args:
            input_dir: 输入数据目录
            output_dir: 输出数据目录
            use_openai: 是否使用OpenAI API
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.use_openai = use_openai
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 加载spaCy中文模型
        try:
            self.nlp = spacy.load('zh_core_web_sm')
            logger.info("已加载spaCy中文模型")
        except Exception as e:
            logger.error(f"加载spaCy中文模型失败: {str(e)}")
            logger.error("请确保已安装: python -m spacy download zh_core_web_sm")
            # 创建一个空的Pipeline作为备用
            self.nlp = spacy.blank('zh')
            logger.warning("使用空的中文Pipeline作为备用")
        
        # 加载jieba
        jieba.initialize()
        logger.info("已加载jieba分词")
        
        # 预定义的知识图谱相关术语 - 移到load_custom_dict()调用之前
        self.kg_terms = [
            "知识图谱", "本体论", "语义网", "RDF", "SPARQL", "图数据库", 
            "三元组", "实体", "关系", "属性", "类别", "子类", "推理", 
            "链接数据", "知识抽取", "知识表示", "知识推理", "知识融合",
            "本体", "词向量", "语义", "查询", "数据挖掘", "机器学习",
            "自然语言处理", "NLP", "实体识别", "命名实体", "关系抽取",
            "知识库", "知识工程", "语义网络", "语义框架", "语义角色",
            "知识表示与推理", "知识获取", "知识发现", "知识计算", "知识问答",
            "图谱构建", "图谱应用", "图谱可视化", "图谱查询", "图谱推理",
            "图谱融合", "图谱存储", "图谱更新", "图谱评估", "图谱标准",
            "语义搜索", "语义推理", "语义标注", "语义计算", "语义集成"
        ]
        
        # 加载自定义词典
        self.load_custom_dict()
        
        # 关系模式
        self.relation_patterns = [
            {"pattern": "是", "relation": "is_a"},
            {"pattern": "包括", "relation": "includes"},
            {"pattern": "包含", "relation": "contains"},
            {"pattern": "属于", "relation": "belongs_to"},
            {"pattern": "由", "relation": "composed_of"},
            {"pattern": "用于", "relation": "used_for"},
            {"pattern": "基于", "relation": "based_on"},
            {"pattern": "应用于", "relation": "applied_to"},
            {"pattern": "定义为", "relation": "defined_as"},
            {"pattern": "等同于", "relation": "equivalent_to"},
            {"pattern": "产生", "relation": "produces"},
            {"pattern": "导致", "relation": "leads_to"},
            {"pattern": "依赖于", "relation": "depends_on"},
            {"pattern": "相关于", "relation": "related_to"},
            {"pattern": "源自", "relation": "derived_from"},
            {"pattern": "影响", "relation": "affects"},
            {"pattern": "支持", "relation": "supports"},
            {"pattern": "实现", "relation": "implements"},
            {"pattern": "扩展", "relation": "extends"},
            {"pattern": "使用", "relation": "uses"}
        ]
        
        # 初始化OpenAI API
        if self.use_openai:
            try:
                # 从环境变量获取API密钥
                openai_api_key = os.environ.get("OPENAI_API_KEY")
                if not openai_api_key:
                    logger.warning("未找到OpenAI API密钥，将不使用OpenAI API")
                    self.use_openai = False
                else:
                    openai.api_key = openai_api_key
                    logger.info("已初始化OpenAI API")
            except Exception as e:
                logger.error(f"初始化OpenAI API失败: {str(e)}")
                self.use_openai = False
    
    def load_custom_dict(self):
        """加载自定义词典"""
        # 创建知识图谱领域词典
        kg_dict_path = os.path.join(self.output_dir, 'kg_dict.txt')
        
        # 如果词典不存在，创建一个
        if not os.path.exists(kg_dict_path):
            with open(kg_dict_path, 'w', encoding='utf-8') as f:
                for term in self.kg_terms:
                    f.write(f"{term} 10 n\n")
            
        # 加载词典
        jieba.load_userdict(kg_dict_path)
        logger.info(f"已加载自定义词典: {kg_dict_path}")
    
    def load_data(self, filename):
        """加载数据文件
        
        Args:
            filename: 文件名
        
        Returns:
            加载的数据
        """
        filepath = os.path.join(self.input_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 对于从agent获取的数据，其结构可能不同，需要特殊处理
            if filename == 'agent_kg_data.json':
                # 确保数据格式一致，每个条目都有所需的字段
                processed_data = []
                for item in data:
                    processed_item = {
                        'title': item.get('title', ''),
                        'url': item.get('url', ''),
                        'summary': item.get('summary', ''),
                        'content': item.get('content', ''),
                        'source': item.get('source', 'agent')
                    }
                    processed_data.append(processed_item)
                return processed_data
            return data
        except Exception as e:
            logger.error(f"加载数据文件 {filepath} 失败: {str(e)}")
            return []
    
    def clean_text(self, text):
        """清洗文本数据
        
        Args:
            text: 原始文本
        
        Returns:
            清洗后的文本
        """
        if not text:
            return ""
            
        # 去除HTML标签
        clean = re.sub(r'<[^>]+>', '', text)
        
        # 去除多余空白字符
        clean = re.sub(r'\s+', ' ', clean)
        
        # 去除特殊字符
        clean = re.sub(r'[^\w\s\u4e00-\u9fff.,，。？?!！:：;；()（）"""\']+', '', clean)
        
        return clean.strip()
    
    def extract_entities_with_jieba(self, text):
        """使用jieba提取实体
        
        Args:
            text: 输入文本
        
        Returns:
            提取的实体列表
        """
        entities = []
        
        # 使用jieba词性标注
        words = pseg.cut(text)
        
        # 提取名词、专有名词等
        for word, flag in words:
            if len(word) > 1 and flag in ['n', 'nr', 'ns', 'nt', 'nz', 'vn']:
                entities.append({
                    'text': word,
                    'label': flag,
                    'type': 'JIEBA'
                })
        
        return entities
    
    def extract_entities_with_regex(self, text):
        """使用正则表达式提取特定模式的实体
        
        Args:
            text: 输入文本
        
        Returns:
            提取的实体列表
        """
        entities = []
        
        # 提取引号中的内容作为可能的术语
        quoted_terms = re.findall(r'[""][^""]+[""]', text)
        for term in quoted_terms:
            clean_term = term.strip('"').strip('"').strip()
            if len(clean_term) > 1:
                entities.append({
                    'text': clean_term,
                    'label': 'QUOTED_TERM',
                    'type': 'REGEX'
                })
        
        # 提取冒号后的内容作为可能的定义
        definitions = re.findall(r'[：:][^。！？.!?，,；;]+', text)
        for definition in definitions:
            clean_def = definition.strip('：').strip(':').strip()
            if len(clean_def) > 1:
                entities.append({
                    'text': clean_def,
                    'label': 'DEFINITION',
                    'type': 'REGEX'
                })
        
        # 提取括号中的内容作为可能的补充说明
        parentheses = re.findall(r'[（(][^）)]+[）)]', text)
        for paren in parentheses:
            clean_paren = paren.strip('（').strip('(').strip('）').strip(')').strip()
            if len(clean_paren) > 1:
                entities.append({
                    'text': clean_paren,
                    'label': 'PARENTHESIS',
                    'type': 'REGEX'
                })
        
        return entities
    
    def extract_entities(self, text):
        """从文本中提取实体
        
        Args:
            text: 输入文本
        
        Returns:
            提取的实体列表
        """
        entities = []
        
        # 使用spaCy提取命名实体
        try:
            # 限制文本长度，避免处理过大的文本
            doc = self.nlp(text[:10000])
            
            # 提取命名实体
            for ent in doc.ents:
                if len(ent.text) > 1:  # 过滤单字实体
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'type': 'NER'
                    })
        except Exception as e:
            logger.warning(f"使用spaCy提取实体失败: {str(e)}")
        
        # 使用jieba提取实体
        jieba_entities = self.extract_entities_with_jieba(text)
        entities.extend(jieba_entities)
        
        # 使用正则表达式提取实体
        regex_entities = self.extract_entities_with_regex(text)
        entities.extend(regex_entities)
        
        # 查找预定义术语
        for term in self.kg_terms:
            if term in text:
                entities.append({
                    'text': term,
                    'label': 'KG_TERM',
                    'type': 'TERM'
                })
        
        # 去重
        unique_entities = []
        seen = set()
        for entity in entities:
            if entity['text'] not in seen:
                seen.add(entity['text'])
                unique_entities.append(entity)
        
        return unique_entities
    
    def extract_relations_with_patterns(self, text, entities):
        """使用模式匹配提取关系
        
        Args:
            text: 输入文本
            entities: 已提取的实体列表
        
        Returns:
            关系三元组列表
        """
        relations = []
        entity_texts = [e['text'] for e in entities]
        
        # 基于模式的关系提取
        for pattern in self.relation_patterns:
            # 查找包含当前关系模式的句子
            sentences = re.split(r'[。！？.!?]', text)
            for sentence in sentences:
                if pattern['pattern'] in sentence:
                    # 寻找句子中的两个实体，它们之间有这种关系
                    for entity1 in entity_texts:
                        if entity1 in sentence:
                            for entity2 in entity_texts:
                                # 避免自关系，并确保实体确实在句子中
                                if entity1 != entity2 and entity2 in sentence:
                                    # 检查是否符合关系模式
                                    if self.check_relation_pattern(sentence, entity1, pattern['pattern'], entity2):
                                        relations.append({
                                            'subject': entity1,
                                            'predicate': pattern['relation'],
                                            'object': entity2,
                                            'sentence': sentence.strip(),
                                            'confidence': 0.8,
                                            'method': 'pattern'
                                        })
        
        return relations
    
    def check_relation_pattern(self, sentence, entity1, relation, entity2):
        """检查句子是否符合关系模式
        
        Args:
            sentence: 句子
            entity1: 主体实体
            relation: 关系词
            entity2: 客体实体
        
        Returns:
            是否符合模式
        """
        # 检查实体1是否在实体2之前
        pos1 = sentence.find(entity1)
        pos2 = sentence.find(entity2)
        
        if pos1 == -1 or pos2 == -1:
            return False
        
        # 检查关系词是否在两个实体之间
        rel_pos = sentence.find(relation, pos1 + len(entity1))
        
        if rel_pos == -1 or rel_pos > pos2:
            # 检查反向关系
            rel_pos = sentence.find(relation, pos2 + len(entity2))
            if rel_pos == -1 or rel_pos > pos1:
                return False
            else:
                # 反向关系，交换主客体
                return False
        
        # 检查关系词是否离实体太远
        if pos2 - (rel_pos + len(relation)) > 20:
            return False
            
        return True
    
    def extract_relations_with_openai(self, text, entities, max_tokens=8000):
        """使用OpenAI API提取关系
        
        Args:
            text: 输入文本
            entities: 已提取的实体列表
            max_tokens: 最大token数
        
        Returns:
            关系三元组列表
        """
        if not self.use_openai or not os.environ.get("OPENAI_API_KEY"):
            logger.warning("OpenAI API不可用，跳过大模型关系抽取")
            return []
            
        relations = []
        
        # 准备实体列表
        entity_texts = [e['text'] for e in entities]
        entity_list = ", ".join(entity_texts[:30])  # 限制实体数量
        
        # 截断文本，避免超出token限制
        if len(text) > max_tokens:
            text = text[:max_tokens]
        
        # 构建提示
        prompt = f"""
请从以下文本中提取实体之间的关系，并以JSON格式返回三元组(主体,关系,客体)。
文本内容: {text}

已识别的实体: {entity_list}

请分析文本，找出这些实体之间的关系。关系类型主要包括（尽可能规约到以下关系）:
- is_a (是一种)
- includes (包括)
- contains (包含)
- belongs_to (属于)
- composed_of (由...组成)
- used_for (用于)
- based_on (基于)
- applied_to (应用于)
- defined_as (定义为)
- equivalent_to (等同于)
- produces (产生)
- leads_to (导致)
- depends_on (依赖于)
- related_to (相关于)
- derived_from (源自)
- affects (影响)
- supports (支持)
- implements (实现)
- extends (扩展)
- uses (使用)
注意，所有的关系类型必须使用英文（例如"is_a"是正确的，但是"是一种"则是错误的），括号里的中文仅供你参考。
请严格按照以下格式返回结果:
[
  {{
    "subject": "实体1",
    "predicate": "关系类型",
    "object": "实体2",
    "sentence": "包含这种关系的原始句子",
    "confidence": 0.9
  }}
]
注意，所有的关系类型必须使用英文（例如"is_a"是正确的，但是"是一种"则是错误的）
只返回JSON数组，不要有其他文字说明。
"""
        
        try:
            # 调用OpenAI API - 更新的API调用方式
            from openai import OpenAI
            client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的知识图谱关系提取助手，擅长从文本中识别实体间的语义关系。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            # 解析响应
            result = response.choices[0].message.content.strip()
            
            try:
                # 直接尝试解析整个JSON
                extracted_relations = json.loads(result)
                for relation in extracted_relations:
                    # 添加方法标记
                    relation['method'] = 'openai'
                    relations.append(relation)
                
                logger.info(f"使用OpenAI API提取了 {len(relations)} 个关系")
            except json.JSONDecodeError:
                # 尝试提取JSON部分
                json_match = re.search(r'\[\s*\{.*\}\s*\]', result, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    try:
                        extracted_relations = json.loads(json_str)
                        for relation in extracted_relations:
                            # 添加方法标记
                            relation['method'] = 'openai'
                            relations.append(relation)
                        
                        logger.info(f"使用OpenAI API提取了 {len(relations)} 个关系")
                    except json.JSONDecodeError as e:
                        logger.error(f"解析OpenAI响应JSON失败: {str(e)}")
                else:
                    logger.warning("OpenAI响应中未找到有效的JSON数据")
                
        except Exception as e:
            logger.error(f"调用OpenAI API失败: {str(e)}")
        
        return relations
    
    def extract_relations(self, text, entities):
        """从文本中提取实体间的关系
        
        Args:
            text: 输入文本
            entities: 已提取的实体列表
        
        Returns:
            实体关系三元组列表
        """
        # 使用模式匹配提取关系
        pattern_relations = self.extract_relations_with_patterns(text, entities)
        
        # 使用OpenAI API提取关系
        openai_relations = []
        if self.use_openai and os.environ.get("OPENAI_API_KEY"):
            logger.info("开始使用OpenAI API提取关系...")
            openai_relations = self.extract_relations_with_openai(text, entities)
            logger.info(f"OpenAI API返回了 {len(openai_relations)} 个关系")
        
        # 合并关系
        all_relations = pattern_relations + openai_relations
        
        # 记录提取结果
        logger.info(f"共提取到 {len(all_relations)} 个关系，其中模式匹配方法: {len(pattern_relations)}，OpenAI方法: {len(openai_relations)}")
        
        return all_relations
    
    def process_file(self, filename):
        """处理单个数据文件
        
        Args:
            filename: 文件名
        
        Returns:
            处理后的实体和关系
        """
        logger.info(f"处理文件: {filename}")
        data = self.load_data(filename)
        
        all_entities = []
        all_relations = []
        
        for item in data:
            # 清洗文本
            summary = self.clean_text(item.get('summary', ''))
            content = self.clean_text(item.get('content', ''))
            
            # 组合文本进行分析
            text = f"{item.get('title', '')}. {summary} {content}"
            
            # 提取实体
            entities = self.extract_entities(text)
            all_entities.extend(entities)
            
            # 提取关系
            relations = self.extract_relations(text, entities)
            all_relations.extend(relations)
        
        return all_entities, all_relations
    
    def merge_and_deduplicate(self, entities_list, relations_list):
        """合并和去重处理后的实体和关系
        
        Args:
            entities_list: 多个文件的实体列表
            relations_list: 多个文件的关系列表
        
        Returns:
            去重后的实体和关系
        """
        # 合并实体
        all_entities = []
        for entities in entities_list:
            all_entities.extend(entities)
        
        # 实体去重
        unique_entities = []
        entity_seen = set()
        for entity in all_entities:
            if entity['text'] not in entity_seen:
                entity_seen.add(entity['text'])
                unique_entities.append(entity)
        
        # 合并关系
        all_relations = []
        for relations in relations_list:
            all_relations.extend(relations)
        
        # 关系去重
        unique_relations = []
        relation_seen = set()
        for relation in all_relations:
            relation_key = f"{relation['subject']}|{relation['predicate']}|{relation['object']}"
            if relation_key not in relation_seen:
                relation_seen.add(relation_key)
                unique_relations.append(relation)
        
        return unique_entities, unique_relations
    
    def save_processed_data(self, entities, relations):
        """保存处理后的数据
        
        Args:
            entities: 实体列表
            relations: 关系列表
        """
        # 保存实体
        entities_file = os.path.join(self.output_dir, 'entities.json')
        with open(entities_file, 'w', encoding='utf-8') as f:
            json.dump(entities, f, ensure_ascii=False, indent=2)
        logger.info(f"实体数据已保存到: {entities_file}, 共 {len(entities)} 个实体")
        
        # 保存关系
        relations_file = os.path.join(self.output_dir, 'relations.json')
        with open(relations_file, 'w', encoding='utf-8') as f:
            json.dump(relations, f, ensure_ascii=False, indent=2)
        logger.info(f"关系数据已保存到: {relations_file}, 共 {len(relations)} 个关系")
        
        # 创建数据框并保存为CSV
        entity_df = pd.DataFrame(entities)
        entity_df.to_csv(os.path.join(self.output_dir, 'entities.csv'), index=False, encoding='utf-8')
        
        relation_df = pd.DataFrame(relations)
        relation_df.to_csv(os.path.join(self.output_dir, 'relations.csv'), index=False, encoding='utf-8')
    
    def run(self):
        """运行处理器处理所有数据"""
        try:
            # json_files = [f for f in os.listdir(self.input_dir) if f.endswith('.json') and ('baidu' in f or 'wiki' in f or 'csdn' in f)]
            json_files = [f for f in os.listdir(self.input_dir) if f.endswith('.json') and ('agent' in f)]
            
            if not json_files:
                logger.error(f"在 {self.input_dir} 目录中没有找到JSON数据文件")
                # 创建一些占位数据以确保后续流程能继续
                self.create_placeholder_data()
                return
            
            entities_list = []
            relations_list = []
            
            for json_file in json_files:
                entities, relations = self.process_file(json_file)
                entities_list.append(entities)
                relations_list.append(relations)
            
            # 合并和去重
            unique_entities, unique_relations = self.merge_and_deduplicate(entities_list, relations_list)
            
            # 保存处理后的数据
            self.save_processed_data(unique_entities, unique_relations)
        except Exception as e:
            logger.error(f"处理器运行失败: {str(e)}")
            # 确保流程不中断
            self.create_placeholder_data()
    
    def create_placeholder_data(self):
        """创建占位数据，确保后续流程能继续"""
        logger.warning("创建占位数据，以确保后续流程能继续")
        
        # 创建占位实体
        placeholder_entities = [
            {"text": "知识图谱", "label": "KG_TERM", "type": "TERM"},
            {"text": "本体论", "label": "KG_TERM", "type": "TERM"},
            {"text": "RDF", "label": "KG_TERM", "type": "TERM"},
            {"text": "SPARQL", "label": "KG_TERM", "type": "TERM"},
            {"text": "知识表示", "label": "KG_TERM", "type": "TERM"}
        ]
        
        # 创建占位关系
        placeholder_relations = [
            {"subject": "知识图谱", "predicate": "includes", "object": "本体论", "sentence": "知识图谱包括本体论", "confidence": 0.9, "method": "placeholder"},
            {"subject": "知识图谱", "predicate": "uses", "object": "RDF", "sentence": "知识图谱使用RDF", "confidence": 0.9, "method": "placeholder"},
            {"subject": "RDF", "predicate": "queried_by", "object": "SPARQL", "sentence": "RDF通过SPARQL查询", "confidence": 0.9, "method": "placeholder"},
            {"subject": "知识图谱", "predicate": "requires", "object": "知识表示", "sentence": "知识图谱需要知识表示", "confidence": 0.9, "method": "placeholder"}
        ]
        
        # 保存占位数据
        self.save_processed_data(placeholder_entities, placeholder_relations)

def main():
    """主函数"""
    processor = KnowledgeProcessor(use_openai=False)  # 默认不使用OpenAI API
    processor.run()

if __name__ == "__main__":
    main() 