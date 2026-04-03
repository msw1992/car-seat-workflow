"""分析节点 - 分析资讯并生成推送内容"""
import os
import json
from typing import List, Any
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from langchain_core.messages import SystemMessage, HumanMessage
from graphs.state import AnalysisNodeInput, AnalysisNodeOutput


def analysis_node(
    state: AnalysisNodeInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> AnalysisNodeOutput:
    """
    title: 资讯分析与内容生成
    desc: 基于搜索结果，以座椅产品规划专家视角进行分析，生成可落地、高价值的创新方向
    integrations: llm
    """
    ctx = runtime.context
    
    # 读取配置文件
    cfg_file = os.path.join(
        os.getenv("COZE_WORKSPACE_PATH"),
        config["metadata"]["llm_cfg"]
    )
    
    with open(cfg_file, "r", encoding="utf-8") as fd:
        _cfg = json.load(fd)
    
    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")
    
    # 准备搜索结果文本
    search_content = ""
    search_results = state.search_results
    
    for idx, result in enumerate(search_results, 1):
        title = result.get("title", "")
        url = result.get("url", "")
        snippet = result.get("snippet", "")
        summary = result.get("summary", "")
        site_name = result.get("site_name", "")
        publish_time = result.get("publish_time", "未知时间")
        
        search_content += f"\n【资讯{idx}】\n"
        search_content += f"标题：{title}\n"
        search_content += f"来源：{site_name}\n"
        search_content += f"发布时间：{publish_time}\n"
        search_content += f"链接：{url}\n"
        search_content += f"摘要：{snippet}\n"
        if summary:
            search_content += f"详细总结：{summary}\n"
        search_content += "-" * 80 + "\n"
    
    # 准备知识库检索结果文本
    knowledge_content = ""
    knowledge_results = state.knowledge_results
    
    if knowledge_results:
        knowledge_content = "\n\n" + "=" * 80 + "\n"
        knowledge_content += "📚 长期记忆库相关知识\n"
        knowledge_content += "=" * 80 + "\n"
        
        for idx, result in enumerate(knowledge_results, 1):
            content_text = result.get("content", "")
            score = result.get("score", 0.0)
            
            knowledge_content += f"\n【知识{idx}】（相关度: {score:.2f}）\n"
            knowledge_content += f"{content_text}\n"
            knowledge_content += "-" * 80 + "\n"
    else:
        knowledge_content = "\n\n（未从长期记忆库检索到相关知识）"
    
    # 使用Jinja2渲染用户提示词
    up_tpl = Template(up)
    user_prompt = up_tpl.render({
        "search_content": search_content,
        "knowledge_content": knowledge_content
    })
    
    # 初始化LLM客户端
    client = LLMClient(ctx=ctx)
    
    # 构建消息
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt)
    ]
    
    # 调用大模型
    response = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.7),
        max_completion_tokens=llm_config.get("max_completion_tokens", 4096)
    )
    
    # 安全提取响应内容
    content = response.content
    if isinstance(content, str):
        analysis_text = content
    elif isinstance(content, list):
        # 处理列表类型的内容
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
        analysis_text = " ".join(text_parts)
    else:
        analysis_text = str(content)
    
    # 构建分析结果
    analysis_result = {
        "raw_content": analysis_text,
        "search_count": len(search_results),
        "knowledge_count": len(knowledge_results),
        "timestamp": ""  # 可以添加时间戳
    }
    
    return AnalysisNodeOutput(analysis_result=analysis_result)
