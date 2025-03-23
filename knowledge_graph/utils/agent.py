from pydantic import BaseModel, SecretStr
from typing import List
import asyncio
from browser_use import Agent, Controller
from langchain_openai import ChatOpenAI
import os

# Define the output format as a Pydantic model


class Post(BaseModel):
    title: str
    url: str
    summary: str
    content: str
    info_box: str
    categories: str
    synonyms: str
    references: str
    source: str


class Posts(BaseModel):
    posts: List[Post]


controller = Controller(output_model=Posts)


async def agent_crawler(topic="知识图谱", pages=5):
    task = f"""
你是一个网页资料搜集专家，你需要爬取和给定主题有关的网页，你需要至少爬取{pages}个有关的网页。现在抓取有关"{topic}"主题的网页。提取关键信息并按照以下格式整理：
1. 标题(title)：提取网页的主标题
2. 网址(url)：提供网页的完整URL
3. 摘要(summary)：用50-100字概括网页的主要内容
4. 正文内容(content)：提取主要文本内容，保留重要段落和关键信息
5. 信息框(info_box)：提取页面中的任何信息框、侧边栏或突出显示的内容
6. 分类(categories)：列出网页所属的所有类别或标签
7. 同义词/相关术语(synonyms)：列出与主题相关的同义词或相关术语
8. 引用/参考(references)：列出页面中引用的所有来源或参考资料
9. 来源(source)：说明信息的来源（例如：维基百科、新闻网站、学术期刊等）
请确保信息准确、完整，并保持原始格式的关键部分。如果有非简体中文内容，一律翻译为简体中文。你应该做适当概括，但是不应该省略内容。你应该适当的访问网页内你认为和{topic}主题有关的链接。
"""
    # model = ChatOpenAI(model='gpt-4o')
    # api_key = "sk-9e5b856d67324a71b82faaaba13ba7dc"
    api_key = 'lm-studio'
    model = ChatOpenAI(base_url='http://localhost:1234/v1', model='gemma-3-27b-it', api_key=SecretStr(api_key))
    agent = Agent(task=task, llm=model, controller=controller)
    
    history = await agent.run()
    
    result = history.final_result()
    
    if result:
        parsed: Posts = Posts.model_validate_json(result)
        print(parsed.posts)
        return parsed.posts
    else:
        print('No result')


if __name__ == '__main__':
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(api_key)
        asyncio.run(agent_crawler())