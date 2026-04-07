# 汽车座椅产品规划每日资讯推送工作流 - 项目复盘

## 目录
1. [项目概述](#项目概述)
2. [技术架构](#技术架构)
3. [工作流搭建过程](#工作流搭建过程)
4. [知识库集成](#知识库集成)
5. [智能知识积累机制](#智能知识积累机制)
6. [知识时效性管理](#知识时效性管理)
7. [问题与解决方案](#问题与解决方案)
8. [部署与运维](#部署与运维)
9. [项目亮点与成果](#项目亮点与成果)
10. [后续优化方向](#后续优化方向)

---

## 项目概述

### 项目背景
作为汽车座椅产品规划团队，需要每日跟踪行业动态、技术创新、用户需求变化等信息。传统人工收集方式效率低、覆盖面窄、难以持续。本项目旨在构建自动化工作流，实现：
- 每日自动搜索行业资讯
- AI 智能分析与知识积累
- 自动推送到团队协作平台

### 核心价值

| 价值维度 | 具体收益 |
|---------|---------|
| **自动化** | 每日自动执行，无需人工干预，节省 1-2 小时/天 |
| **智能化** | AI 分析 + 知识库积累，建议质量持续提升 |
| **零成本** | GitHub Actions + cron-job.org 免费方案，零服务器成本 |
| **闭环迭代** | 知识自动积累，形成正向循环 |

### 项目目标
1. 每日自动搜索汽车座椅领域最新资讯
2. 结合历史知识进行智能分析
3. 生成结构化的产品规划建议报告
4. 自动推送到飞书群
5. 高价值内容自动沉淀到知识库

---

## 技术架构

### 技术栈

| 层级 | 技术选型 | 说明 |
|------|---------|------|
| 编程语言 | Python 3.12 | 类型安全，生态丰富 |
| 工作流框架 | LangGraph 1.0.2 | DAG 编排，状态管理 |
| AI 能力 | coze-coding-dev-sdk | LLM、Web Search、Knowledge |
| 定时调度 | APScheduler + cron-job.org | 稳定的定时触发 |
| HTTP 服务 | FastAPI | 轻量级 API 框架 |
| 部署平台 | GitHub Actions | 免费的 CI/CD 平台 |

### 系统架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     定时触发 (cron-job.org)                       │
│                           ↓                                      │
│                    GitHub Actions                                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      LangGraph 工作流                            │
│                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐     │
│  │ 搜索节点  │ → │ 知识检索  │ → │ 分析节点  │ → │ 飞书推送  │     │
│  │          │   │          │   │          │   │          │     │
│  │ Web搜资讯 │   │ 检索历史  │   │ AI分析   │   │ 推送报告  │     │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘     │
│                                      ↓                          │
│                              ┌──────────┐                       │
│                              │ 知识保存  │                       │
│                              │ 智能沉淀  │                       │
│                              └──────────┘                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                       外部服务                                    │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐         │
│  │ Web搜素  │   │ 知识库   │   │ 大模型   │   │  飞书   │         │
│  │  API    │   │  API    │   │  API    │   │ Webhook │         │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘         │
└─────────────────────────────────────────────────────────────────┘
```

### 节点功能详解

| 节点名称 | 输入 | 输出 | 核心功能 |
|---------|------|------|---------|
| search_node | 搜索关键词 | 资讯列表(20条) | Web 搜索，时间过滤 |
| knowledge_search_node | 资讯列表 | 知识列表(10条) | 知识库相似度检索 |
| analysis_node | 资讯+知识 | 分析报告 | LLM 综合分析 |
| feishu_push_node | 分析报告 | 推送状态 | 格式化推送 |
| save_knowledge_node | 分析报告 | 保存状态 | 智能筛选保存 |

---

## 工作流搭建过程

### 阶段一：基础工作流搭建

#### 1.1 状态定义 (state.py)
```python
# 全局状态
class GlobalState(BaseModel):
    search_results: List[dict] = []      # 搜索结果
    knowledge_results: List[dict] = []   # 知识库结果
    analysis_result: dict = {}           # 分析结果
    push_status: str = ""                # 推送状态
    save_status: str = ""                # 保存状态

# 图输入/输出
class GraphInput(BaseModel):
    pass  # 无需外部输入

class GraphOutput(BaseModel):
    analysis_result: dict
    push_status: str
    save_status: str
```

#### 1.2 节点实现
- **搜索节点**: 调用 Web Search API，获取最新资讯
- **分析节点**: 调用 LLM，生成结构化报告
- **推送节点**: 调用飞书 Webhook，推送报告

#### 1.3 主图编排 (graph.py)
```python
builder = StateGraph(GlobalState, input_schema=GraphInput, output_schema=GraphOutput)

builder.add_node("search", search_node)
builder.add_node("analysis", analysis_node)
builder.add_node("push", feishu_push_node)

builder.set_entry_point("search")
builder.add_edge("search", "analysis")
builder.add_edge("analysis", "push")
builder.add_edge("push", END)
```

### 阶段二：部署方案选择

#### 2.1 方案对比

| 方案 | 成本 | 稳定性 | 维护难度 | 最终选择 |
|------|------|-------|---------|---------|
| 自建服务器 | 高 | 中 | 高 | ❌ |
| 云函数 (SCF/Lambda) | 中 | 高 | 中 | ❌ |
| **GitHub Actions** | 免费 | 中 | 低 | ✅ |

#### 2.2 GitHub Actions 配置要点
- 使用 `repository_dispatch` 支持外部触发
- 配置 Secrets 存储敏感信息
- 轻量级依赖避免编译失败

---

## 知识库集成

### 为什么需要知识库？

**痛点**:
- 每次分析都是"从零开始"，无法利用历史经验
- 重复分析相同主题，效率低下
- 有价值的洞察容易流失

**解决方案**:
- 集成 Coze 长期记忆库 (Knowledge)
- 每次分析前检索相关知识
- 分析结果智能保存，持续积累

### 知识库创建过程

#### 步骤 1: 创建知识库表
```python
from coze_coding_dev_sdk import KnowledgeClient

client = KnowledgeClient(ctx=ctx)

# 创建知识库
response = client.create_table(
    table_name="Car_Seat",
    description="汽车座椅产品规划知识库"
)
```

#### 步骤 2: 知识库检索节点 (knowledge_search_node.py)

**核心逻辑**:
```python
def knowledge_search_node(state, config, runtime):
    client = KnowledgeClient(ctx=ctx)
    
    # 从搜索结果提取关键词
    query = "汽车座椅 产品规划 智能座舱 AI技术"
    
    # 检索相关知识
    response = client.search(
        query=query,
        table_names=["Car_Seat"],
        top_k=10,
        min_score=0.5  # 相似度阈值
    )
    
    return KnowledgeSearchNodeOutput(knowledge_results=results)
```

**设计考量**:
| 参数 | 值 | 原因 |
|------|-----|------|
| top_k | 10 | 平衡覆盖度与噪音 |
| min_score | 0.5 | 过滤低相关内容 |

#### 步骤 3: 工作流集成

更新工作流，在分析前增加知识检索:
```python
builder.add_node("search", search_node)
builder.add_node("knowledge_search", knowledge_search_node)  # 新增
builder.add_node("analysis", analysis_node)

builder.add_edge("search", "knowledge_search")
builder.add_edge("knowledge_search", "analysis")
```

### 知识库检索效果

| 维度 | 无知识库 | 有知识库 |
|------|---------|---------|
| 分析深度 | 仅基于当前资讯 | 结合历史经验 |
| 建议质量 | 可能重复 | 持续优化 |
| 知识复用 | 无 | 自动关联 |

---

## 智能知识积累机制

### 设计理念

**问题**: 不是所有内容都值得保存
- 日常新闻：时效性短，几天后过时
- 重复内容：知识库可能已有类似知识
- 低质量信息：缺乏数据支撑

**方案**: AI 智能筛选 + 多重过滤

### 保存节点设计 (save_knowledge_node.py)

#### 三重过滤机制

```
┌─────────────────────────────────────────────────────────┐
│                     分析报告内容                          │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  第一重过滤：AI 价值评估                                   │
│  - 行业趋势？技术案例？用户洞察？项目经验？                │
│  - 置信度评分 > 0.7 才进入下一步                          │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  第二重过滤：相似度检测                                   │
│  - 检索知识库中相似内容                                   │
│  - 相似度 < 0.85 才保存（避免重复）                       │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  第三重过滤：元数据增强                                   │
│  - 添加知识类型、保存时间、置信度                         │
│  - 便于后续时效性管理                                     │
└─────────────────────────────────────────────────────────┘
                         ↓
                    保存到知识库
```

#### 核心代码实现

**第一重：AI 价值评估**
```python
judge_prompt = """请判断以下内容是否值得保存到知识库。

✅ 推荐保存：
- 重要的行业趋势报告（具有长期参考价值）
- 创新技术案例分析（可复用的技术方案）
- 用户需求洞察总结（深度用户研究结论）
- 成功/失败的项目经验（有借鉴意义）

❌ 不推荐保存：
- 日常新闻资讯（时效性短）
- 重复或相似内容
- 低质量或未验证的信息

返回 JSON: {"should_save": true/false, "value_type": "类型", "confidence": 0.8}
"""
```

**第二重：相似度检测**
```python
search_response = knowledge_client.search(
    query=search_query,
    table_names=[knowledge_table],
    top_k=3,
    min_score=0.85  # 高相似度阈值
)

if any(chunk.score >= 0.85 for chunk in search_response.chunks):
    return "跳过保存：已有相似内容"
```

**第三重：元数据增强**
```python
knowledge_content = f"""【{value_type}】汽车座椅产品规划日报 - {current_date}

{raw_content}

---
知识类型: {value_type}
评估置信度: {confidence}
保存时间: {current_date}
"""
```

### 知识保存效果统计

| 指标 | 数值 |
|------|------|
| 平均每日分析报告 | 1 份 |
| AI 判断值得保存率 | ~30% |
| 相似度过滤率 | ~20% |
| 最终保存率 | ~25% |
| 知识库增长率 | 约 1-2 条/周 |

---

## 知识时效性管理

### 设计背景

**问题**: 知识库中的内容会过时
- 行业趋势：半年后可能过时
- 竞品分析：3个月后需要更新
- 技术案例：可能长期有效

**目标**: 建立知识时效性管理机制

### 时效性策略设计

#### 知识保留策略
```python
RETENTION_POLICY = {
    "行业趋势": 180,      # 6个月
    "技术案例": 365,      # 1年
    "用户洞察": 365,      # 1年
    "项目经验": -1,       # 永久保留
    "竞品分析": 90,       # 3个月
    "其他": 180           # 默认6个月
}
```

### 知识清理工具 (cleanup_knowledge.py)

#### 过期判断逻辑
```python
def is_expired(content: str) -> tuple:
    # 1. 解析保存时间
    save_date = parse_save_date(content)  # 从内容中提取
    
    # 2. 解析知识类型
    knowledge_type = parse_knowledge_type(content)
    
    # 3. 计算过期日期
    retention_days = RETENTION_POLICY.get(knowledge_type, 180)
    expiry_date = save_date + timedelta(days=retention_days)
    
    # 4. 判断是否过期
    return datetime.now() > expiry_date
```

#### 清理脚本
```bash
# 模拟运行（不实际删除）
python scripts/cleanup_knowledge.py --dry-run

# 实际执行清理
python scripts/cleanup_knowledge.py
```

### 当前方案与未来规划

| 阶段 | 方案 | 状态 |
|------|------|------|
| 当前 | 在保存时添加元数据（类型、时间） | ✅ 已实现 |
| 当前 | 清理脚本支持过期检测 | ✅ 已实现 |
| 未来 | 知识库 SDK 支持删除 API 后自动清理 | ⏳ 待实现 |
| 未来 | 检索时动态过滤过期知识 | ⏳ 待实现 |

---

## 问题与解决方案

### 问题 1: GitHub Actions schedule 不触发

**现象**:
```yaml
on:
  schedule:
    - cron: '35 1 * * *'  # 配置正确但不执行
```

**排查过程**:
1. 检查 cron 语法 → 正确
2. 调整配置顺序 → 无效
3. 添加 push 触发器 → 无效
4. 创建干净测试 workflow → 仍不触发

**根因**: GitHub Actions 的 schedule 触发器在免费仓库中不稳定，可能延迟或跳过

**最终方案**: 使用 cron-job.org 作为外部定时触发器

```
cron-job.org → GitHub API (repository_dispatch) → workflow 执行
```

**配置要点**:
```yaml
on:
  repository_dispatch:
    types: [daily-trigger]
  push:
    branches: [main]
```

### 问题 2: 环境变量未传递

**现象**: 手动运行时报错 `COZE_WORKLOAD_IDENTITY_API_KEY 未设置`

**原因**: GitHub Actions 中环境变量需要在步骤中显式导出到 `$GITHUB_ENV`

**解决方案**:
```yaml
- name: Configure Token
  run: |
    echo "COZE_WORKLOAD_IDENTITY_API_KEY=$COZE_WORKLOAD_IDENTITY_API_KEY" >> $GITHUB_ENV
```

### 问题 3: cozeloop 追踪报错 401

**现象**: 运行时出现 401 认证错误

**原因**: 沙箱环境外的 cozeloop 追踪功能认证问题

**解决方案**: 禁用追踪功能
```yaml
env:
  COZELOOP_DISABLED: "true"
```

### 问题 4: 推送资讯包含过时内容

**现象**: 推送的日报参考资料中包含发布时间超过规定范围的资讯

**原因**: 
1. 搜索节点的时间过滤函数在无法解析时间时返回 `True`（保留）
2. 分析节点未验证资讯时间有效性

**解决方案**:

| 层级 | 修改 | 效果 |
|------|------|------|
| 搜索节点 | 严格过滤，无法解析时间时丢弃 | 减少无效资讯 |
| 分析节点 | 添加发布时间字段 | LLM 可感知时间 |
| LLM 提示词 | 只分析近 3 个月资讯 | 双重保障 |

**代码变更**:
```python
# 修改前：宽松过滤
if not publish_time:
    return True  # 保留

# 修改后：严格过滤
if not publish_time:
    return False  # 丢弃

# 新增：必须是过去的时间
return 0 <= time_diff <= days
```

### 问题 5: SDK 环境变量命名

**现象**: 知识库操作失败，提示 workspace_id 无效

**排查**: SDK 使用 `COZE_PROJECT_SPACE_ID` 获取 workspace_id，而非 `COZE_WORKSPACE_ID`

**解决方案**: 更新环境变量名称
```yaml
env:
  COZE_PROJECT_SPACE_ID: ${{ secrets.COZE_PROJECT_SPACE_ID }}
```

---

## 部署与运维

### GitHub Secrets 清单

| Secret 名称 | 说明 | 获取方式 |
|------------|------|---------|
| `COZE_WORKLOAD_IDENTITY_API_KEY` | 沙箱 Token | 沙箱环境变量 |
| `COZE_PROJECT_SPACE_ID` | 工作空间 ID | Coze 平台 |
| `FEISHU_WEBHOOK_URL` | 飞书群机器人 | 飞书群设置 |
| `KNOWLEDGE_TABLE_NAME` | 知识库名称 | 手动创建 |

### cron-job.org 配置

| 配置项 | 值 |
|-------|-----|
| URL | `https://api.github.com/repos/xxx/dispatches` |
| Method | POST |
| Cron | `35 1 * * *` (北京时间 9:35) |
| Header | `Authorization: token YOUR_PAT` |
| Header | `Content-Type: application/json` |
| Body | `{"event_type": "daily-trigger"}` |

### 监控与告警

| 监控项 | 方式 | 告警阈值 |
|--------|------|---------|
| workflow 执行状态 | GitHub Actions 日志 | 失败 |
| 执行时长 | 日志分析 | > 10分钟 |
| 知识库增长 | 定期检查 | 连续7天无新增 |

### 运维命令

```bash
# 手动触发 workflow
gh workflow run daily_push.yml

# 查看执行日志
gh run watch

# 清理知识库（模拟）
python scripts/cleanup_knowledge.py --dry-run

# 测试知识库访问
python scripts/test_knowledge_access.py
```

---

## 项目亮点与成果

### 技术亮点

| 亮点 | 说明 |
|------|------|
| **零成本部署** | GitHub Actions + cron-job.org 完全免费 |
| **智能知识积累** | AI 筛选 + 三重过滤，保证知识质量 |
| **时效性管理** | 按知识类型设置不同保留策略 |
| **闭环迭代** | 知识持续积累，分析质量不断提升 |

### 业务价值

| 价值 | 量化指标 |
|------|---------|
| 时间节省 | 约 1-2 小时/天 |
| 信息覆盖 | 20+ 条/天 |
| 知识积累 | 约 1-2 条/周 |
| 建议质量 | 持续提升（知识库增长后） |

### 可复用性

本项目架构可快速复用到其他领域：
- 更换搜索关键词 → 适配其他行业
- 调整分析提示词 → 适配其他场景
- 知识库独立配置 → 多项目并行

---

## 后续优化方向

### 短期优化 (1-2周)

| 优化项 | 预期效果 |
|--------|---------|
| 内容质量评估 | 过滤低质量、营销性质内容 |
| 站点权威性判断 | 优先保留权威站点内容 |
| 推送格式优化 | 更好的可读性和交互 |

### 中期优化 (1-2月)

| 优化项 | 预期效果 |
|--------|---------|
| 知识库自动清理 | SDK 支持后自动删除过期知识 |
| 多渠道推送 | 支持企业微信、钉钉 |
| 反馈机制 | 用户反馈闭环，优化筛选策略 |

### 长期规划 (3-6月)

| 优化项 | 预期效果 |
|--------|---------|
| 竞品监控 | 自动跟踪竞品动态 |
| 趋势预测 | 基于历史数据预测趋势 |
| 多 Agent 协作 | 专业分工，深度分析 |

---

## 附录

### 项目文件结构

```
car-seat-workflow/
├── .github/workflows/
│   ├── daily_push.yml              # 主工作流
│   └── test-clean.yml              # 测试工作流
├── src/
│   ├── graphs/
│   │   ├── state.py                # 状态定义
│   │   ├── graph.py                # 主图编排
│   │   └── nodes/
│   │       ├── search_node.py      # 搜索节点
│   │       ├── knowledge_search_node.py  # 知识检索节点
│   │       ├── analysis_node.py    # 分析节点
│   │       ├── feishu_push_node.py # 飞书推送节点
│   │       └── save_knowledge_node.py    # 知识保存节点
│   ├── scheduler/
│   │   └── scheduler.py            # 定时调度服务
│   └── main.py                     # 入口文件
├── config/
│   └── seat_analysis_llm_cfg.json  # LLM 配置
├── scripts/
│   ├── cleanup_knowledge.py        # 知识清理脚本
│   ├── reset_knowledge.py          # 知识库重置
│   └── test_knowledge_access.py    # 知识库测试
├── docs/
│   ├── CRON_JOB_ORG_GUIDE.md       # cron-job.org 配置指南
│   └── GITHUB_SECRETS_CHECKLIST.md # Secrets 配置清单
├── requirements-github-actions.txt # 轻量级依赖
├── PROJECT_SUMMARY_FOR_PPT.md      # 项目总结
└── PROJECT_REVIEW_FOR_PPT.md       # 本文档
```

### 关键代码片段索引

| 功能 | 文件位置 |
|------|---------|
| 时间过滤函数 | `src/graphs/nodes/search_node.py:12-53` |
| 知识库检索 | `src/graphs/nodes/knowledge_search_node.py:59-77` |
| AI 价值评估 | `src/graphs/nodes/save_knowledge_node.py:40-100` |
| 相似度检测 | `src/graphs/nodes/save_knowledge_node.py:109-149` |
| 时效性策略 | `scripts/cleanup_knowledge.py:15-22` |

### 参考文档

- [LangGraph 官方文档](https://langchain-ai.github.io/langgraph/)
- [coze-coding-dev-sdk 文档](https://github.com/coze-dev/coze-coding-dev-sdk)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [cron-job.org 使用指南](https://cron-job.org/en/documentation/)

---

**文档版本**: v1.0  
**最后更新**: 2025年1月  
**作者**: AI 工作流搭建专家
