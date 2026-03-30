"""飞书推送节点 - 将分析结果推送到飞书"""
import json
from typing import Dict, Any
import requests
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import FeishuPushNodeInput, FeishuPushNodeOutput


def get_webhook_url() -> str:
    """获取飞书webhook URL"""
    from coze_workload_identity import Client
    client = Client()
    wechat_bot_credential = client.get_integration_credential("integration-feishu-message")
    webhook_url = json.loads(wechat_bot_credential)["webhook_url"]
    return webhook_url


def feishu_push_node(
    state: FeishuPushNodeInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> FeishuPushNodeOutput:
    """
    title: 飞书消息推送
    desc: 将分析结果以富文本消息形式推送到飞书群
    integrations: feishu-message
    """
    ctx = runtime.context
    
    # 获取分析结果
    analysis_result = state.analysis_result
    raw_content = analysis_result.get("raw_content", "")
    search_count = analysis_result.get("search_count", 0)
    
    # 构建推送内容
    title = "🚗 每日汽车座椅产品规划资讯推送"
    
    # 使用富文本格式
    content_lines = [
        [{"tag": "text", "text": f"📊 本次共分析 {search_count} 条资讯\n\n"}],
        [{"tag": "text", "text": raw_content}]
    ]
    
    payload = {
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": title,
                    "content": content_lines
                }
            }
        }
    }
    
    try:
        # 发送请求
        webhook_url = get_webhook_url()
        response = requests.post(webhook_url, json=payload, timeout=30)
        response_data = response.json()
        
        # 检查响应
        if response.status_code == 200 and response_data.get("StatusCode") == 0:
            push_status = "推送成功"
        else:
            error_msg = response_data.get("msg", "未知错误")
            push_status = f"推送失败: {error_msg}"
            
    except Exception as e:
        push_status = f"推送异常: {str(e)}"
    
    return FeishuPushNodeOutput(push_status=push_status)
