"""搜索节点 - 搜索汽车座椅产品规划资讯"""
import json
from datetime import datetime, timedelta
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
    
    # 定义权威汽车行业站点白名单（用于优先排序，而非强制过滤）
    # 包含用户指定的站点 + 推荐站点
    priority_sites = {
        "autohome.com.cn", "dongchedi.com", "gasgoo.com", "sohu.com",
        "autoreport.cn", "d1ev.com", "yiche.com", "news18a.com"
    }
    
    # 定义搜索关键词列表（扩展到8个，覆盖更多领域）
    search_queries = [
        "汽车座椅 产品规划 最新动态",
        "智能座舱 座椅创新 AI技术",
        "汽车座椅 新材料 新技术",
        "新能源汽车 座椅设计 用户需求",
        "汽车座椅 供应商 定点 量产",      # 供应链动态
        "汽车座椅 安全法规 标准",          # 法规政策
        "汽车座椅 人机工程 舒适性",        # 人机工程
        "汽车座椅 轻量化 环保材料"         # 轻量化趋势
    ]
    
    # 收集所有搜索结果
    all_results: List[Any] = []
    
    # 执行多个搜索查询
    for query in search_queries:
        try:
            response = client.search(
                query=query,
                search_type="web",
                count=10,  # 每个查询返回10条结果
                need_summary=True,
                time_range="1w"  # 搜索最近一周的资讯
            )
            
            if response.web_items:
                for item in response.web_items:
                    # 判断是否来自权威站点
                    site_name = item.site_name if item.site_name else ""
                    is_priority = any(domain in site_name for domain in priority_sites)
                    
                    result_item = {
                        "title": item.title if item.title else "",
                        "url": item.url if item.url else "",
                        "snippet": item.snippet if item.snippet else "",
                        "summary": item.summary if item.summary else "",
                        "site_name": site_name,
                        "publish_time": item.publish_time if item.publish_time else "",
                        "is_priority_site": is_priority  # 标记是否为权威站点
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
    
    # 过滤最近一周的资讯（双重保险）
    one_week_ago = datetime.now() - timedelta(days=7)
    recent_results: List[Any] = []
    
    for result in unique_results:
        publish_time = result.get("publish_time", "")
        if publish_time:
            try:
                # 尝试解析发布时间
                # 常见格式：2024-03-30, 2024/03/30, 2024年03月30日
                publish_date = None
                for fmt in ["%Y-%m-%d", "%Y/%m/%d", "%Y年%m月%d日"]:
                    try:
                        publish_date = datetime.strptime(publish_time.strip(), fmt)
                        break
                    except ValueError:
                        continue
                
                # 如果能解析出日期，检查是否在一周内
                if publish_date and publish_date >= one_week_ago:
                    recent_results.append(result)
                elif not publish_date:
                    # 无法解析日期的结果也保留（可能是最新发布）
                    recent_results.append(result)
            except Exception:
                # 解析失败的结果保留
                recent_results.append(result)
        else:
            # 没有发布时间的结果也保留
            recent_results.append(result)
    
    # 优先排序：权威站点的结果排在前面
    priority_results = sorted(
        recent_results,
        key=lambda x: (
            not x.get("is_priority_site", False),  # 权威站点优先（False排前面）
            x.get("publish_time", ""),              # 发布时间倒序
        )
    )
    
    # 限制结果数量为20条
    final_results = priority_results[:20]
    
    # 打印统计信息
    priority_count = sum(1 for r in final_results if r.get("is_priority_site"))
    print(f"搜索统计: 共获取 {len(all_results)} 条结果, 去重后 {len(unique_results)} 条, 过滤后 {len(recent_results)} 条, 最终 {len(final_results)} 条 (其中权威站点 {priority_count} 条)")
    
    return SearchNodeOutput(search_results=final_results)
