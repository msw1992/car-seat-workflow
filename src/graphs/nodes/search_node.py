"""搜索节点 - 搜索汽车座椅产品规划资讯"""
import json
from typing import List, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import SearchClient
from graphs.state import SearchNodeInput, SearchNodeOutput


def search_node(
    state: SearchNodeInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SearchNodeOutput:
    """
    title: 汽车座椅资讯搜索
    desc: 搜索汽车座椅产品规划相关的最新资讯，包括智能座舱、新材料、AI技术应用等领域
    integrations: web-search
    """
    ctx = runtime.context
    
    # 初始化搜索客户端
    client = SearchClient(ctx=ctx)
    
    # 定义搜索关键词列表
    search_queries = [
        "汽车座椅 产品规划 最新动态",
        "智能座舱 座椅创新 AI技术",
        "汽车座椅 新材料 新技术",
        "新能源汽车 座椅设计 用户需求"
    ]
    
    # 收集所有搜索结果
    all_results: List[Any] = []
    
    # 执行多个搜索查询
    for query in search_queries:
        try:
            response = client.search(
                query=query,
                search_type="web",
                count=8,  # 每个查询返回8条结果
                need_summary=True,
                time_range="1w"  # 搜索最近一周的资讯
            )
            
            if response.web_items:
                for item in response.web_items:
                    result_item = {
                        "title": item.title if item.title else "",
                        "url": item.url if item.url else "",
                        "snippet": item.snippet if item.snippet else "",
                        "summary": item.summary if item.summary else "",
                        "site_name": item.site_name if item.site_name else "",
                        "publish_time": item.publish_time if item.publish_time else ""
                    }
                    all_results.append(result_item)
        except Exception as e:
            # 记录错误但继续执行其他搜索
            print(f"搜索查询 '{query}' 失败: {str(e)}")
            continue
    
    # 去重（基于URL）
    unique_results: List[Any] = []
    seen_urls: set = set()
    
    for result in all_results:
        url = result.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_results.append(result)
    
    # 限制结果数量，扩大到20条
    final_results = unique_results[:20]
    
    return SearchNodeOutput(search_results=final_results)
