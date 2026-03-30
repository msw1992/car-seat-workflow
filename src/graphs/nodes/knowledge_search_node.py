"""知识库检索节点 - 从长期记忆库检索相关内容"""
import os
import json
from typing import List, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import KnowledgeClient
from graphs.state import KnowledgeSearchNodeInput, KnowledgeSearchNodeOutput


def knowledge_search_node(
    state: KnowledgeSearchNodeInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> KnowledgeSearchNodeOutput:
    """
    title: 知识库检索
    desc: 从Coze长期记忆库Car_Seat中检索与汽车座椅相关的历史知识和经验
    integrations: knowledge
    """
    ctx = runtime.context
    
    # 初始化知识库客户端
    client = KnowledgeClient(ctx=ctx)
    
    # 从网络搜索结果中提取关键词用于知识库检索
    search_keywords = []
    for result in state.search_results[:5]:  # 只取前5条提取关键词
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        # 简单提取关键词（实际可以用NLP提取）
        if title:
            search_keywords.append(title)
    
    # 构建检索查询
    query = "汽车座椅 产品规划 智能座舱 AI技术 新材料 用户需求"
    if search_keywords:
        query = " ".join(search_keywords[:3])  # 取前3个标题作为查询
    
    # 获取知识库名称（优先级：环境变量 > 配置文件 > 默认值）
    knowledge_table = os.getenv("KNOWLEDGE_TABLE_NAME")
    
    if not knowledge_table:
        # 尝试从配置文件读取
        config_path = "data/knowledge_table.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                    knowledge_table = config_data.get("table_name", "Car_Seat")
            except Exception:
                knowledge_table = "Car_Seat"
        else:
            knowledge_table = "Car_Seat"
    
    knowledge_results: List[Any] = []
    
    try:
        # 从指定的知识库检索相关内容
        response = client.search(
            query=query,
            table_names=[knowledge_table],  # 指定知识库
            top_k=10,  # 检索10条相关知识
            min_score=0.5  # 相似度阈值
        )
        
        if response.code == 0 and response.chunks:
            for chunk in response.chunks:
                knowledge_item = {
                    "content": chunk.content if chunk.content else "",
                    "score": chunk.score if chunk.score else 0.0,
                    "doc_id": chunk.doc_id if chunk.doc_id else ""
                }
                knowledge_results.append(knowledge_item)
                
            print(f"✅ 从知识库 '{knowledge_table}' 检索到 {len(knowledge_results)} 条相关知识")
        else:
            print(f"⚠️  知识库 '{knowledge_table}' 未检索到相关知识（可能是新知识库）")
            
    except Exception as e:
        # 记录错误但继续执行
        print(f"❌ 知识库检索失败: {str(e)}")
        # 知识库检索失败不影响整体流程
    
    return KnowledgeSearchNodeOutput(
        search_results=state.search_results,
        knowledge_results=knowledge_results
    )
