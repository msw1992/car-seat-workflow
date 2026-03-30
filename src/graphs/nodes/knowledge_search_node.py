"""知识库检索节点 - 从长期记忆库检索相关内容"""
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
    desc: 从Coze长期记忆库中检索与汽车座椅相关的历史知识和经验
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
    
    knowledge_results: List[Any] = []
    
    try:
        # 从知识库检索相关内容
        response = client.search(
            query=query,
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
    except Exception as e:
        # 记录错误但继续执行
        print(f"知识库检索失败: {str(e)}")
        # 知识库检索失败不影响整体流程
    
    return KnowledgeSearchNodeOutput(
        search_results=state.search_results,
        knowledge_results=knowledge_results
    )
