"""智能知识保存节点 - 筛选并保存高价值内容到知识库"""
import os
import json
from typing import List, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import KnowledgeClient, LLMClient, KnowledgeDocument, DataSourceType
from langchain_core.messages import SystemMessage, HumanMessage
from graphs.state import SaveKnowledgeNodeInput, SaveKnowledgeNodeOutput


def save_knowledge_node(
    state: SaveKnowledgeNodeInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SaveKnowledgeNodeOutput:
    """
    title: 智能知识保存
    desc: 使用AI判断分析结果是否值得保存到知识库，并自动添加高价值内容
    integrations: llm, knowledge
    """
    ctx = runtime.context
    
    # 获取分析结果
    analysis_result = state.analysis_result
    raw_content = analysis_result.get("raw_content", "")
    
    # 如果分析内容为空，直接返回
    if not raw_content:
        return SaveKnowledgeNodeOutput(
            save_status="跳过保存：分析内容为空",
            saved_content=""
        )
    
    # 初始化LLM客户端
    llm_client = LLMClient(ctx=ctx)
    
    # 步骤1: 使用LLM判断是否值得保存
    judge_prompt = f"""请判断以下汽车座椅产品规划分析报告是否值得保存到知识库。

判断标准：

✅ 推荐保存的内容：
- 重要的行业趋势报告（具有长期参考价值）
- 创新技术案例分析（可复用的技术方案）
- 用户需求洞察总结（深度用户研究结论）
- 成功/失败的项目经验（有借鉴意义）
- 竞品分析报告（深度对比分析）

❌ 不推荐保存的内容：
- 日常新闻资讯（时效性短，几天后就过时）
- 重复或相似内容（知识库可能已有类似知识）
- 低质量或未验证的信息（缺乏数据支撑）
- 与座椅无关的内容（超出专业领域）

待评估内容：
{raw_content[:2000]}  # 截取前2000字符评估

请以JSON格式返回评估结果：
{{
    "should_save": true/false,
    "reason": "判断理由",
    "value_type": "行业趋势/技术案例/用户洞察/项目经验/竞品分析/其他",
    "confidence": 0.0-1.0
}}

只返回JSON，不要有其他内容。"""

    try:
        # 调用LLM判断
        messages = [
            SystemMessage(content="你是一个知识管理专家，擅长判断内容的知识价值。"),
            HumanMessage(content=judge_prompt)
        ]
        
        response = llm_client.invoke(
            messages=messages,
            model="doubao-seed-1-8-251228",
            temperature=0.3
        )
        
        # 解析判断结果
        content = response.content
        if isinstance(content, list):
            content = " ".join([item.get("text", "") if isinstance(item, dict) else str(item) for item in content])
        
        try:
            judge_result = json.loads(content.strip())
        except json.JSONDecodeError:
            # JSON解析失败，默认不保存
            return SaveKnowledgeNodeOutput(
                save_status="跳过保存：评估结果解析失败",
                saved_content=""
            )
        
        should_save = judge_result.get("should_save", False)
        reason = judge_result.get("reason", "")
        value_type = judge_result.get("value_type", "其他")
        confidence = judge_result.get("confidence", 0.0)
        
        # 如果不值得保存，直接返回
        if not should_save:
            return SaveKnowledgeNodeOutput(
                save_status=f"跳过保存：{reason}",
                saved_content=""
            )
        
        # 步骤2: 检查知识库中是否已有相似内容
        knowledge_client = KnowledgeClient(ctx=ctx)
        
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
        
        # 提取关键内容进行相似度检索
        search_query = raw_content[:200]  # 用前200字符检索
        
        try:
            search_response = knowledge_client.search(
                query=search_query,
                table_names=[knowledge_table],
                top_k=3,
                min_score=0.85  # 相似度阈值0.85，避免重复
            )
            
            # 如果已有高度相似的内容，跳过保存
            if search_response.code == 0 and search_response.chunks:
                for chunk in search_response.chunks:
                    if chunk.score >= 0.85:
                        return SaveKnowledgeNodeOutput(
                            save_status=f"跳过保存：知识库中已有相似内容（相似度: {chunk.score:.2f}）",
                            saved_content=""
                        )
        except Exception as e:
            print(f"⚠️  相似度检索失败: {str(e)}")
            # 检索失败不影响后续流程
        
        # 步骤3: 保存到知识库
        # 构建知识内容（添加元数据）
        from datetime import datetime
        current_date = datetime.now().strftime("%Y年%m月%d日")
        
        knowledge_content = f"""【{value_type}】汽车座椅产品规划日报 - {current_date}

{raw_content}

---
知识类型: {value_type}
评估置信度: {confidence}
保存时间: {current_date}
"""
        
        try:
            # 添加到知识库
            docs = [
                KnowledgeDocument(
                    source=DataSourceType.TEXT,
                    raw_data=knowledge_content
                )
            ]
            
            add_response = knowledge_client.add_documents(
                documents=docs,
                table_name=knowledge_table
            )
            
            if add_response.code == 0:
                save_status = f"✅ 已保存到知识库（类型: {value_type}，置信度: {confidence:.2f}）"
                saved_content = knowledge_content[:200] + "..."
                
                print(f"✅ {save_status}")
            else:
                save_status = f"❌ 保存失败: {add_response.msg}"
                saved_content = ""
                
        except Exception as e:
            save_status = f"❌ 保存异常: {str(e)}"
            saved_content = ""
            
        return SaveKnowledgeNodeOutput(
            save_status=save_status,
            saved_content=saved_content
        )
        
    except Exception as e:
        return SaveKnowledgeNodeOutput(
            save_status=f"❌ 智能评估失败: {str(e)}",
            saved_content=""
        )
