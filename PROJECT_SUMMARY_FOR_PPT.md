# 汽车座椅产品规划每日资讯推送工作流

## 项目概述

### 项目背景
基于 LangGraph 的汽车座椅产品规划自动化工作流，实现资讯搜索、知识库检索、AI 分析、飞书推送及智能知识积累的完整闭环。

### 核心价值
- **自动化**: 每日自动搜索、分析、推送，无需人工干预
- **智能化**: AI 分析 + 知识库积累，持续优化建议质量
- **零成本**: GitHub Actions + cron-job.org 免费部署

---

## 技术架构

### 技术栈
| 技术 | 用途 |
|------|------|
| Python 3.12 | 主语言 |
| LangGraph 1.0.2 | 工作流编排 |
| coze-coding-dev-sdk | Web Search, Knowledge, LLM |
| APScheduler | 定时调度 |
| FastAPI | HTTP 服务 |

### 工作流程
```
搜索节点 → 知识库检索节点 → 分析节点 → 飞书推送节点 → 智能保存节点
```

### 节点功能
| 节点 | 功能 |
|------|------|
| search_node | 搜索汽车座椅产品规划相关资讯（20条） |
| knowledge_search_node | 从 Coze 长期记忆库检索相关知识（10条） |
| analysis_node | 结合网络资讯和知识库，生成产品规划建议 |
| feishu_push_node | 将分析结果推送到飞书群 |
| save_knowledge_node | 智能筛选并保存高价值内容到知识库 |

---

## 关键决策

### 1. 部署方案选择
- **方案**: GitHub Actions（免费、零服务器）
- **原因**: 
  - 完全免费（每月 2000 分钟额度）
  - 零服务器维护
  - 代码更新自动部署

### 2. Token 配置
- **使用**: 沙箱环境的 `dmpl` 格式 Token
- **环境变量**: `COZE_WORKLOAD_IDENTITY_API_KEY`
- **关键发现**: SDK 使用 `COZE_PROJECT_SPACE_ID` 获取 workspace_id，而非 `COZE_WORKSPACE_ID`

### 3. 依赖管理
- **创建**: `requirements-github-actions.txt`
- **原因**: 避免无法编译的包导致 GitHub Actions 失败

### 4. 定时任务方案
- **问题**: GitHub Actions 的 `schedule` 触发器不稳定
- **解决**: 使用 cron-job.org 作为外部定时触发器

---

## 问题与解决方案

### 问题 1: GitHub Actions schedule 不触发

**现象**:
```yaml
on:
  schedule:
    - cron: '35 1 * * *'  # 配置正确但不执行
```

**尝试方案**:
1. ❌ 调整配置顺序
2. ❌ 添加 push 触发器
3. ❌ 创建干净的测试 workflow

**最终方案**:
使用 cron-job.org 通过 `repository_dispatch` 触发 workflow

```yaml
on:
  repository_dispatch:
    types: [daily-trigger]
  push:
    branches: [main]
```

### 问题 2: 环境变量未传递

**现象**: 手动运行时报错 `COZE_WORKLOAD_IDENTITY_API_KEY 未设置`

**原因**: GitHub Actions 中环境变量需要在步骤中显式导出

**解决方案**:
```yaml
- name: Configure Token
  run: |
    echo "COZE_WORKLOAD_IDENTITY_API_KEY=$COZE_WORKLOAD_IDENTITY_API_KEY" >> $GITHUB_ENV
```

### 问题 3: cozeloop 追踪报错

**现象**: 401 认证错误

**原因**: 沙箱环境外的 cozeloop 追踪功能认证问题

**解决方案**:
```yaml
env:
  COZELOOP_DISABLED: "true"
```

### 问题 4: 推送资讯包含过时内容

**现象**: 推送的日报参考资料中包含发布时间超过规定范围的资讯

**原因**: 
1. 搜索节点的时间过滤函数在无法解析时间时返回 `True`（保留），导致老旧资讯被错误保留
2. 分析节点未验证资讯时间有效性

**解决方案**:
1. **搜索节点**：修改 `is_within_time_range` 函数，无法解析时间时返回 `False`（丢弃），严格过滤
2. **分析节点**：在搜索内容中添加发布时间字段
3. **LLM提示词**：添加时间验证要求，只分析最近3个月内的资讯

```python
# 修改前：宽松过滤
if not publish_time:
    return True  # 保留

# 修改后：严格过滤
if not publish_time:
    return False  # 丢弃
```

**时间范围配置**:
- 搜索策略：1周 → 1个月 → 3个月（优先获取最新资讯）
- 分析过滤：只保留最近3个月内的资讯

---

## 部署配置

### GitHub Secrets 清单

| Secret 名称 | 说明 |
|------------|------|
| `COZE_WORKLOAD_IDENTITY_API_KEY` | 沙箱 Token（dmpl 格式） |
| `COZE_PROJECT_SPACE_ID` | 工作空间 ID |
| `FEISHU_WEBHOOK_URL` | 飞书群机器人 Webhook |
| `KNOWLEDGE_TABLE_NAME` | 知识库名称 |

### cron-job.org 配置

| 配置项 | 值 |
|-------|-----|
| URL | `https://api.github.com/repos/msw1992/car-seat-workflow/dispatches` |
| Method | POST |
| Cron | `35 1 * * *` (北京时间 9:35) |
| Header | `Authorization: token YOUR_PAT` |
| Header | `Content-Type: application/json` |
| Body | `{"event_type": "daily-trigger"}` |

---

## 文件结构

```
car-seat-workflow/
├── .github/workflows/
│   └── daily_push.yml          # GitHub Actions 配置
├── src/
│   ├── graphs/
│   │   ├── state.py            # 状态定义
│   │   ├── graph.py            # 主图编排
│   │   └── nodes/              # 节点实现
│   ├── scheduler/              # 定时调度服务
│   └── main.py                 # 入口
├── config/
│   └── seat_analysis_llm_cfg.json  # LLM 配置
├── docs/
│   ├── CRON_JOB_ORG_GUIDE.md   # cron-job.org 配置指南
│   └── ...
├── requirements-github-actions.txt  # 轻量级依赖
└── AGENTS.md                   # 项目结构索引
```

---

## 运行效果

### 输出内容
工作流每日在飞书群推送：

- 📈 **今日趋势洞察**: 行业动态分析
- 💡 **创新方向建议**: 3-5 个可落地的产品创新方向
- 🔍 **重点关注**: AI 技术与座椅结合应用
- 📚 **参考资料**: 信息来源链接

### 知识积累
- 自动保存高价值内容
- 避免重复和低质量信息
- 知识库持续完善

---

## 项目亮点

1. **完全自动化**: 从搜索到推送，全流程无人值守
2. **零成本部署**: GitHub Actions + cron-job.org 免费方案
3. **智能知识库**: 自动积累高质量内容，持续优化分析质量
4. **灵活触发**: 支持定时、手动、推送多种触发方式
5. **容错设计**: 禁用非核心功能追踪，避免认证问题影响主流程

---

## 后续优化方向

1. **知识库管理**: 添加知识过期清理机制
2. **推送渠道**: 扩展支持企业微信、钉钉等
3. **分析深度**: 增加竞品对比、用户画像分析
4. **监控告警**: 添加运行状态监控和异常告警

---

## 参考文档

- [cron-job.org 配置指南](docs/CRON_JOB_ORG_GUIDE.md)
- [GitHub Secrets 配置清单](docs/GITHUB_SECRETS_CHECKLIST.md)
- [COZE_API_KEY 获取指南](docs/COZE_API_KEY_GUIDE.md)
- [免费部署方案对比](docs/FREE_DEPLOYMENT_GUIDE.md)
