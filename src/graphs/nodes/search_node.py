"""搜索节点 - 搜索汽车座椅产品规划资讯"""
import json
from typing import List, Any
from datetime import datetime, timedelta
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import SearchClient
from graphs.state import SearchNodeInput, SearchNodeOutput


def is_within_time_range(publish_time: str, days: int) -> bool:
    """
    检查发布时间是否在指定天数内
    
    Args:
        publish_time: 发布时间字符串
        days: 天数阈值
    
    Returns:
        bool: 是否在时间范围内
    """
    if not publish_time:
        return True  # 如果没有时间信息，暂时保留
    
    try:
        # 尝试解析多种时间格式
        time_formats = [
            "%Y-%m-%d",
            "%Y年%m月%d日",
            "%Y/%m/%d",
            "%Y.%m.%d"
        ]
        
        pub_date = None
        for fmt in time_formats:
            try:
                pub_date = datetime.strptime(publish_time, fmt)
                break
            except ValueError:
                continue
        
        if not pub_date:
            return True  # 解析失败，暂时保留
        
        # 计算时间差
        now = datetime.now()
        time_diff = (now - pub_date).days
        
        return time_diff <= days
        
    except Exception:
        return True  # 异常情况，暂时保留


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
    
    # 定义目标结果数量
    target_count = 20
    
    # 定义时间范围策略（优先级从高到低）
    time_ranges = ["1w", "1m"]  # 一周 -> 一个月
    time_range_days = {"1w": 7, "1m": 30}
    
    # 收集所有搜索结果
    all_results: List[Any] = []
    
    print(f"🔍 开始搜索汽车座椅资讯（目标: {target_count}条）")
    
    # 按时间范围策略搜索
    for time_range in time_ranges:
        print(f"\n📅 尝试搜索时间范围: {time_range} ({time_range_days[time_range]}天)")
        
        # 清空当前轮次的结果
        current_results: List[Any] = []
        
        # 执行多个搜索查询
        for query in search_queries:
            try:
                response = client.search(
                    query=query,
                    search_type="web",
                    count=8,  # 每个查询返回8条结果
                    need_summary=True,
                    time_range=time_range
                )
                
                if response.web_items:
                    for item in response.web_items:
                        publish_time = item.publish_time if item.publish_time else ""
                        
                        # 严格过滤时间范围
                        if is_within_time_range(publish_time, time_range_days[time_range]):
                            result_item = {
                                "title": item.title if item.title else "",
                                "url": item.url if item.url else "",
                                "snippet": item.snippet if item.snippet else "",
                                "summary": item.summary if item.summary else "",
                                "site_name": item.site_name if item.site_name else "",
                                "publish_time": publish_time
                            }
                            current_results.append(result_item)
                            
            except Exception as e:
                print(f"⚠️  搜索查询 '{query}' 失败: {str(e)}")
                continue
        
        # 去重（基于URL）
        unique_current: List[Any] = []
        seen_urls: set = set()
        
        for result in current_results:
            url = result.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_current.append(result)
        
        print(f"   找到 {len(unique_current)} 条符合时间范围的资讯")
        
        # 合并到总结果中
        for result in unique_current:
            url = result.get("url", "")
            # 检查是否已在总结果中
            if url and not any(r.get("url") == url for r in all_results):
                all_results.append(result)
        
        # 检查是否达到目标数量
        if len(all_results) >= target_count:
            print(f"\n✅ 已达到目标数量 ({len(all_results)}条)")
            break
    
    # 最终结果
    final_results = all_results[:target_count]
    
    print(f"\n📊 搜索统计：")
    print(f"   总计获取: {len(all_results)}条")
    print(f"   最终保留: {len(final_results)}条")
    
    # 显示时间分布
    time_distribution: dict = {}
    for result in final_results:
        pub_time = result.get("publish_time", "未知")
        if pub_time:
            # 提取日期部分
            if len(pub_time) >= 10:
                date_str = pub_time[:10]
            else:
                date_str = pub_time
            time_distribution[date_str] = time_distribution.get(date_str, 0) + 1
    
    if time_distribution:
        print(f"\n📅 资讯时间分布：")
        for date, count in sorted(time_distribution.items(), reverse=True)[:5]:
            print(f"   {date}: {count}条")
    
    return SearchNodeOutput(search_results=final_results)
