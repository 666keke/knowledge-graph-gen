import os
import json
import re
import time
import requests
from bs4 import BeautifulSoup
import logging
import asyncio
from urllib.parse import urljoin, urlparse
from knowledge_graph.utils.agent import agent_crawler

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KnowledgeGraphCrawler:
    """知识图谱爬虫类，用于抓取关于知识图谱的数据"""
    def __init__(self, output_dir='knowledge_graph/data', use_agent=1, use_trad_method=1):
        """初始化爬虫
        
        Args:
            output_dir: 数据保存目录
        """
        self.output_dir = output_dir
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.baidu_base_url = 'https://baike.baidu.com'
        self.wiki_base_url = 'https://zh.wikipedia.org'
        self.zhihu_base_url = 'https://www.zhihu.com'
        self.csdn_base_url = 'https://blog.csdn.net'
        self.visited_urls = set()
        self.use_agent = use_agent
        self.use_trad_method = use_trad_method
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def fetch_page(self, url):
        """获取页面内容
        
        Args:
            url: 要抓取的URL
        
        Returns:
            BeautifulSoup对象或None（如果请求失败）
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            
            # 检测并设置正确的编码
            if response.encoding == 'ISO-8859-1':
                response.encoding = response.apparent_encoding
                
            return BeautifulSoup(response.text, 'lxml')
        except Exception as e:
            logger.error(f"抓取页面 {url} 失败: {str(e)}")
            return None
    
    def crawl_baidu_baike(self, keyword='知识图谱', max_pages=20):
        """抓取百度百科关于知识图谱的内容
        
        Args:
            keyword: 要搜索的关键词
            max_pages: 最大抓取页面数
        
        Returns:
            抓取的数据列表
        """
        start_url = f"{self.baidu_base_url}/item/{keyword}"
        results = []
        queue = [start_url]
        
        logger.info(f"开始抓取百度百科，关键词: {keyword}")
        
        page_count = 0
        while queue and page_count < max_pages:
            current_url = queue.pop(0)
            
            # 如果已经访问过，则跳过
            if current_url in self.visited_urls:
                continue
                
            logger.info(f"正在抓取: {current_url}")
            self.visited_urls.add(current_url)
            
            soup = self.fetch_page(current_url)
            if not soup:
                continue
                
            # 获取标题
            title = soup.find('h1').get_text().strip() if soup.find('h1') else "Unknown Title"
            
            # 获取摘要
            summary_elem = soup.find('div', class_='lemma-summary')
            summary = summary_elem.get_text().strip() if summary_elem else ""
            
            # 获取正文内容
            content_elem = soup.find('div', class_='main-content')
            content = content_elem.get_text().strip() if content_elem else ""
            
            # 获取基本信息表
            info_box = {}
            info_elem = soup.find('div', class_='basic-info')
            if info_elem:
                dt_elems = info_elem.find_all('dt', class_='basicInfo-item name')
                dd_elems = info_elem.find_all('dd', class_='basicInfo-item value')
                
                for dt, dd in zip(dt_elems, dd_elems):
                    key = dt.get_text().strip()
                    value = dd.get_text().strip()
                    info_box[key] = value
            
            # 获取分类信息
            categories = []
            category_elem = soup.find('div', class_='lemmaWgt-lemmaCatalog')
            if category_elem:
                category_links = category_elem.find_all('a')
                for link in category_links:
                    categories.append(link.get_text().strip())
            
            # 获取同义词和相关术语
            synonyms = []
            polysemant_elem = soup.find('ul', class_='polysemantList-wrapper')
            if polysemant_elem:
                synonym_links = polysemant_elem.find_all('a')
                for link in synonym_links:
                    synonyms.append(link.get_text().strip())
            
            # 获取参考资料和引用
            references = []
            reference_elem = soup.find('dl', class_='lemma-reference')
            if reference_elem:
                ref_items = reference_elem.find_all('li')
                for item in ref_items:
                    ref_text = item.get_text().strip()
                    references.append(ref_text)
            
            # 存储数据
            page_data = {
                'title': title,
                'url': current_url,
                'summary': summary,
                'content': content,
                'info_box': info_box,
                'categories': categories,
                'synonyms': synonyms,
                'references': references,
                'source': 'baidu_baike'
            }
            
            results.append(page_data)
            page_count += 1
            
            # 获取相关链接
            related_links = []
            
            # 获取正文中的链接
            if content_elem:
                content_links = content_elem.find_all('a', href=re.compile('^/item/'))
                related_links.extend(content_links)
            
            # 获取"参见"部分的链接
            see_also_elem = soup.find('span', string=re.compile('参见|参考|相关|另见'))
            if see_also_elem and see_also_elem.parent:
                see_also_links = see_also_elem.parent.find_all('a', href=re.compile('^/item/'))
                related_links.extend(see_also_links)
            
            # 获取底部相关链接
            bottom_related = soup.find('div', class_='lemma-reference')
            if bottom_related:
                bottom_links = bottom_related.find_all('a', href=re.compile('^/item/'))
                related_links.extend(bottom_links)
            
            # 添加到队列
            for link in related_links[:10]:  # 限制相关链接数量
                href = link.get('href')
                if href:
                    next_url = urljoin(self.baidu_base_url, href)
                    if next_url not in self.visited_urls:
                        queue.append(next_url)
            
            # 休眠一段时间，避免请求过于频繁
            time.sleep(1)
        
        logger.info(f"百度百科抓取完成，共抓取 {len(results)} 页")
        return results
    
    def crawl_wikipedia(self, keyword='知识图谱', max_pages=10):
        """抓取维基百科关于知识图谱的内容
        
        Args:
            keyword: 要搜索的关键词
            max_pages: 最大抓取页面数
        
        Returns:
            抓取的数据列表
        """
        # 构建搜索URL
        search_url = f"{self.wiki_base_url}/wiki/{keyword}"
        results = []
        queue = [search_url]
        wiki_visited = set()
        
        logger.info(f"开始抓取维基百科，关键词: {keyword}")
        
        page_count = 0
        while queue and page_count < max_pages:
            current_url = queue.pop(0)
            
            # 如果已经访问过，则跳过
            if current_url in wiki_visited:
                continue
                
            logger.info(f"正在抓取: {current_url}")
            wiki_visited.add(current_url)
            
            soup = self.fetch_page(current_url)
            if not soup:
                continue
                
            # 获取标题
            title = soup.find('h1', id='firstHeading').get_text().strip() if soup.find('h1', id='firstHeading') else "Unknown Title"
            
            # 获取摘要
            summary = ""
            content_div = soup.find('div', id='mw-content-text')
            if content_div:
                first_p = content_div.find('p', class_=None)
                if first_p:
                    summary = first_p.get_text().strip()
            
            # 获取正文内容
            content = ""
            if content_div:
                paragraphs = content_div.find_all('p')
                content = "\n".join([p.get_text().strip() for p in paragraphs])
            
            # 获取信息框
            info_box = {}
            infobox = soup.find('table', class_='infobox')
            if infobox:
                rows = infobox.find_all('tr')
                for row in rows:
                    header = row.find('th')
                    data = row.find('td')
                    if header and data:
                        key = header.get_text().strip()
                        value = data.get_text().strip()
                        info_box[key] = value
            
            # 获取分类
            categories = []
            category_links = soup.find_all('a', href=re.compile('^/wiki/Category:'))
            for link in category_links:
                categories.append(link.get_text().strip())
            
            # 存储数据
            page_data = {
                'title': title,
                'url': current_url,
                'summary': summary,
                'content': content,
                'info_box': info_box,
                'categories': categories,
                'source': 'wikipedia'
            }
            
            results.append(page_data)
            page_count += 1
            
            # 获取相关链接
            if content_div:
                content_links = content_div.find_all('a', href=re.compile('^/wiki/(?!File:|Wikipedia:|Help:|Special:|Talk:)'))
                for link in content_links[:5]:  # 限制相关链接数量
                    href = link.get('href')
                    if href:
                        next_url = urljoin(self.wiki_base_url, href)
                        if next_url not in wiki_visited:
                            queue.append(next_url)
            
            # 休眠一段时间，避免请求过于频繁
            time.sleep(1.5)
        
        logger.info(f"维基百科抓取完成，共抓取 {len(results)} 页")
        return results
    
    def crawl_csdn_blogs(self, keyword='知识图谱', max_pages=5):
        """抓取CSDN博客关于知识图谱的内容
        
        Args:
            keyword: 要搜索的关键词
            max_pages: 最大抓取页面数
        
        Returns:
            抓取的数据列表
        """
        search_url = f"https://so.csdn.net/so/search/s.do?q={keyword}&t=blog"
        results = []
        
        logger.info(f"开始抓取CSDN博客，关键词: {keyword}")
        
        # 获取搜索结果页
        soup = self.fetch_page(search_url)
        if not soup:
            logger.error("抓取CSDN搜索页失败")
            return results
        
        # 提取博客链接
        blog_links = []
        article_items = soup.find_all('div', class_='blog-list-box')
        for item in article_items:
            link_elem = item.find('a', class_='blog-title')
            if link_elem and link_elem.get('href'):
                blog_links.append(link_elem.get('href'))
        
        # 限制抓取数量
        blog_links = blog_links[:max_pages]
        
        # 抓取每篇博客
        for blog_url in blog_links:
            logger.info(f"正在抓取CSDN博客: {blog_url}")
            
            blog_soup = self.fetch_page(blog_url)
            if not blog_soup:
                continue
            
            # 获取标题
            title = blog_soup.find('h1', class_='title-article').get_text().strip() if blog_soup.find('h1', class_='title-article') else "Unknown Title"
            
            # 获取作者
            author = ""
            author_elem = blog_soup.find('a', class_='follow-nickName')
            if author_elem:
                author = author_elem.get_text().strip()
            
            # 获取发布时间
            publish_time = ""
            time_elem = blog_soup.find('span', class_='time')
            if time_elem:
                publish_time = time_elem.get_text().strip()
            
            # 获取正文内容
            content = ""
            content_elem = blog_soup.find('div', id='article_content')
            if content_elem:
                content = content_elem.get_text().strip()
            
            # 获取标签
            tags = []
            tag_elems = blog_soup.find_all('a', class_='tag-link')
            for tag in tag_elems:
                tags.append(tag.get_text().strip())
            
            # 存储数据
            blog_data = {
                'title': title,
                'url': blog_url,
                'author': author,
                'publish_time': publish_time,
                'content': content,
                'tags': tags,
                'source': 'csdn_blog'
            }
            
            results.append(blog_data)
            
            # 休眠一段时间，避免请求过于频繁
            time.sleep(2)
        
        logger.info(f"CSDN博客抓取完成，共抓取 {len(results)} 篇")
        return results
    
    def crawl_browser_use(self, keyword='知识图谱', max_pages=5):
        results = asyncio.run(agent_crawler(topic=keyword, pages=max_pages))
        # results = await agent_crawler(topic=keyword, pages=max_pages)
        logger.info(f"Agent 运行完毕，共抓取 {len(results)} 篇")
        return results

    def save_data(self, data, filename):
        """保存抓取的数据到文件
        
        Args:
            data: 要保存的数据
            filename: 文件名
        """
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"数据已保存到: {filepath}")
    
    def run(self):
        """运行爬虫"""
        # 抓取百度百科
        baidu_data = self.crawl_baidu_baike(keyword='知识图谱', max_pages=10)
        self.save_data(baidu_data, 'baidu_kg_data.json')
        
        if(self.use_trad_method):
            # 抓取维基百科
            try:
                wiki_data = self.crawl_wikipedia(keyword='知识图谱', max_pages=5)
                self.save_data(wiki_data, 'wiki_kg_data.json')
            except Exception as e:
                logger.error(f"抓取维基百科失败: {str(e)}")
            
            # 抓取CSDN博客
            try:
                csdn_data = self.crawl_csdn_blogs(keyword='知识图谱', max_pages=5)
                self.save_data(csdn_data, 'csdn_kg_data.json')
            except Exception as e:
                logger.error(f"抓取CSDN博客失败: {str(e)}")

            # 抓取相关概念的数据
            related_keywords = [
                '本体论', '语义网', 'RDF', '图数据库', 'SPARQL', '知识表示', 
                '知识推理', '知识抽取', '实体识别', '关系抽取', '知识融合', 
                '链接数据', '知识问答', '知识计算', '知识工程'
            ]
        
            for keyword in related_keywords:
                logger.info(f"抓取相关概念: {keyword}")
                self.visited_urls = set()  # 重置已访问URL集合
                related_data = self.crawl_wikipedia(keyword=keyword, max_pages=1)
                # related_data = self.crawl_baidu_baike(keyword=keyword, max_pages=5)
                self.save_data(related_data, f'wikipedia_{keyword}_data.json')

        if(self.use_agent):
            try:
                agent_data = self.crawl_browser_use(keyword='知识图谱', max_pages=10)
                with open('agent_kg_data.json', 'w', encoding='utf-8') as f:
                    f.write(agent_data)
                logger.info(f"数据已保存到: agent_kg_data.json")
            except Exception as e:
                logger.error(f"Agent运行失败: {str(e)}")
        

def main():
    """主函数"""
    crawler = KnowledgeGraphCrawler(use_agent=1, use_trad_method=1)
    crawler.run()

if __name__ == "__main__":
    main() 