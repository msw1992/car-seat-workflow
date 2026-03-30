"""主图编排 - 汽车座椅产品规划资讯推送工作流"""
from langgraph.graph import StateGraph, END
from graphs.state import (
    GlobalState,
    GraphInput,
    GraphOutput
)
from graphs.nodes.search_node import search_node
from graphs.nodes.analysis_node import analysis_node
from graphs.nodes.feishu_push_node import feishu_push_node


# 创建状态图
builder = StateGraph(
    GlobalState,
    input_schema=GraphInput,
    output_schema=GraphOutput
)

# 添加节点
builder.add_node("search_node", search_node)
builder.add_node(
    "analysis_node",
    analysis_node,
    metadata={
        "type": "agent",
        "llm_cfg": "config/seat_analysis_llm_cfg.json"
    }
)
builder.add_node("feishu_push_node", feishu_push_node)

# 设置入口点
builder.set_entry_point("search_node")

# 添加边
builder.add_edge("search_node", "analysis_node")
builder.add_edge("analysis_node", "feishu_push_node")
builder.add_edge("feishu_push_node", END)

# 编译图
main_graph = builder.compile()
