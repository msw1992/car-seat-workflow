"""工作流状态定义"""
from typing import List, Optional
from pydantic import BaseModel, Field


class GlobalState(BaseModel):
    """全局状态定义"""
    search_results: List[dict] = Field(default=[], description="搜索结果列表")
    analysis_result: dict = Field(default={}, description="分析后的结构化结果")
    push_status: str = Field(default="", description="推送状态")


class GraphInput(BaseModel):
    """工作流输入"""
    pass


class GraphOutput(BaseModel):
    """工作流输出"""
    push_status: str = Field(..., description="推送状态")
    analysis_result: dict = Field(..., description="分析结果")


class SearchNodeInput(BaseModel):
    """搜索节点输入"""
    pass


class SearchNodeOutput(BaseModel):
    """搜索节点输出"""
    search_results: List[dict] = Field(..., description="搜索结果列表")


class AnalysisNodeInput(BaseModel):
    """分析节点输入"""
    search_results: List[dict] = Field(..., description="搜索结果列表")


class AnalysisNodeOutput(BaseModel):
    """分析节点输出"""
    analysis_result: dict = Field(..., description="分析后的结构化结果")


class FeishuPushNodeInput(BaseModel):
    """飞书推送节点输入"""
    analysis_result: dict = Field(..., description="分析结果")


class FeishuPushNodeOutput(BaseModel):
    """飞书推送节点输出"""
    push_status: str = Field(..., description="推送状态")
