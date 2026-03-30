# 汽车座椅产品规划每日资讯推送工作流 - 项目总结

> 本文档可直接导入豆包、Kimi等AI工具生成PPT

---

## 一、项目背景与目标

### 1.1 业务需求

- **核心目标**：每日自动推送汽车座椅产品规划资讯到飞书群
- **目标用户**：汽车座椅产品规划团队
- **使用场景**：每日晨会前获取最新行业动态

### 1.2 功能需求

| 需求项 | 具体要求 |
|-------|---------|
| 资讯来源 | 网络搜索 + 知识库检索 |
| 搜索范围 | 最近一周，20条资讯 |
| 分析深度 | 产品规划专家视角，包含趋势洞察和创新建议 |
| 推送时间 | 每天早上8:30 |
| 推送渠道 | 飞书群 |
| 知识积累 | 自动保存高价值内容到知识库 |

### 1.3 技术选型

- **工作流框架**：LangGraph 1.0
- **开发语言**：Python 3.12
- **AI能力**：豆包大模型（LLM + Web Search + Knowledge）
- **调度方式**：APScheduler + 后台服务

---

## 二、技术架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                     定时调度服务                              │
│                  (每天8:30触发)                               │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   工作流主服务 (HTTP)                         │
│                    http://localhost:5000                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              LangGraph 工作流 (DAG)                          │
│                                                              │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐ │
│  │  搜索节点  │→ │ 知识库   │→ │  分析节点  │→ │ 飞书推送  │ │
│  │ (Web)    │   │ 检索节点  │   │  (LLM)   │   │   节点    │ │
│  └──────────┘   └──────────┘   └──────────┘   └─────┬────┘ │
│                                                      │       │
│                                                      ▼       │
│                                              ┌──────────┐   │
│                                              │ 智能保存  │   │
│                                              │   节点    │   │
│                                              └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 核心节点设计

| 节点名称 | 输入 | 输出 | 核心能力 |
|---------|------|------|---------|
| 搜索节点 | - | 20条资讯 | Web Search + 时间过滤 |
| 知识库检索节点 | 资讯列表 | 10条相关知识 | Knowledge Search |
| 分析节点 | 资讯+知识 | 结构化报告 | LLM分析 |
| 飞书推送节点 | 分析报告 | 推送状态 | Feishu API |
| 智能保存节点 | 分析报告 | 保存状态 | LLM判断 + Knowledge存储 |

### 2.3 数据流转

```
网络资讯 (20条) ─┐
                 ├→ AI分析 → 结构化报告 → 飞书推送
知识库 (10条) ───┘                           ↓
                                       高价值内容
                                           ↓
                                      知识库保存
```

---

## 三、遇到的核心问题与解决方案

### 3.1 定时调度问题

#### 问题描述
```
问题：使用AsyncIOScheduler启动定时服务报错
错误：RuntimeError: no running event loop
原因：事件循环在后台线程中初始化失败
```

#### 解决方案
```python
# ❌ 错误方案
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler()

# ✅ 正确方案
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
```

**经验总结**：
- 后台定时任务应使用BackgroundScheduler而非AsyncIOScheduler
- 明确指定时区避免时区混乱
- 添加信号处理机制优雅退出

---

### 3.2 知识库删除限制问题

#### 问题描述
```
需求：删除知识库中2026年3月之前的知识
问题：SDK不支持删除API
影响：知识库会无限增长，无法清理过期内容
```

#### 解决方案

**方案：创建新知识库并切换**

```python
# 1. 创建新知识库（带时间戳）
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
new_table = f"Car_Seat_{timestamp}"

# 2. 初始化新知识库
knowledge_client.add_documents(
    documents=[...],
    table_name=new_table
)

# 3. 更新配置文件，切换到新知识库
config_data = {"table_name": new_table}
with open("data/knowledge_table.json", 'w') as f:
    json.dump(config_data, f)
```

**配置优先级**：
```
环境变量 > 配置文件 > 默认值
```

**经验总结**：
- SDK能力有限时，采用替代方案而非死磕
- 配置要灵活，支持多种切换方式
- 记录新旧知识库的映射关系

---

### 3.3 搜索站点限制问题

#### 问题描述
```
需求：仅在指定站点（汽车之家、懂车帝等）搜索
测试：带站点限制搜索 → 无结果
原因：站点限制+时间限制+关键词，三重过滤过于严格
```

#### 测试对比

| 搜索方式 | 时间范围 | 结果 |
|---------|---------|------|
| 全网搜索 | 最近一周 | ✅ 有结果 |
| 站点限制 | 最近一周 | ❌ 无结果 |

#### 解决方案

**采用质量后评估策略**

```python
# 搜索时：全网搜索，不限制站点
response = client.search(
    query=query,
    search_type="web",
    time_range="1w"
    # ❌ 不使用 sites 参数
)

# 分析时：AI评估内容质量和站点权威性
judge_prompt = """
请判断以下内容的权威性和价值：
- 来源站点是否为权威汽车媒体
- 内容是否有数据支撑
- 是否具有长期参考价值
"""
```

**经验总结**：
- 功能限制可能导致无结果时，优先保证可用性
- 通过AI后处理弥补功能限制
- 记录用户需求，未来SDK改进时再实现

---

### 3.4 搜索时间过滤问题

#### 问题描述
```
问题：参考资料中有publish_time为2025年的内容
要求：只保留最近一周的内容，不足则放宽到一个月
```

#### 解决方案

**动态时间范围策略**

```python
# 定义时间范围优先级
time_ranges = ["1w", "1m"]  # 一周 -> 一个月
time_range_days = {"1w": 7, "1m": 30}

# 动态调整
for time_range in time_ranges:
    results = search_with_time_range(time_range)
    if len(results) >= 20:
        break  # 达到目标数量，停止搜索
```

**严格时间校验**

```python
def is_within_time_range(publish_time: str, days: int) -> bool:
    """
    检查发布时间是否在指定天数内
    支持多种时间格式：YYYY-MM-DD、YYYY年MM月DD日等
    """
    # 解析时间
    pub_date = parse_publish_time(publish_time)
    
    # 计算时间差
    time_diff = (datetime.now() - pub_date).days
    
    return time_diff <= days
```

**经验总结**：
- API的time_range参数不一定准确，需要二次校验
- 支持多种时间格式提高兼容性
- 动态策略保证结果数量

---

### 3.5 后台运行问题

#### 问题描述
```
问题：执行 bash start_scheduler.sh 后关闭网页，定时任务停止
原因：进程是前台进程，关闭终端会发送SIGHUP信号终止进程
```

#### 解决方案对比

| 启动方式 | 关闭网页后 | 实现方式 |
|---------|-----------|---------|
| `bash start_scheduler.sh` | ❌ 会停止 | 前台进程 |
| `bash start_scheduler_daemon.sh` | ✅ 继续运行 | nohup后台进程 |
| systemd服务 | ✅ 继续运行 | 系统服务 |

**后台运行实现**

```bash
#!/bin/bash
# start_scheduler_daemon.sh

# 使用nohup后台运行
nohup python src/scheduler/scheduler_service.py \
    >> /tmp/seat_push_scheduler.log 2>&1 &

# 记录PID
SCHEDULER_PID=$!
echo "$SCHEDULER_PID" > /tmp/seat_push_scheduler.pid
```

**进程守护特性**

```python
# scheduler_service.py
# 父进程ID = 1 表示已脱离终端
# 关闭网页/终端后进程继续运行
```

**经验总结**：
- 生产环境必须使用后台运行方式
- 记录PID方便管理
- 提供启停脚本简化操作
- 推荐使用systemd实现开机自启

---

## 四、关键技术决策

### 4.1 为什么选择独立定时服务？

**方案对比**

| 方案 | 优点 | 缺点 |
|-----|------|------|
| 工作流内置定时节点 | 简单 | 灵活性差，难以调试 |
| **独立定时服务** | ✅ 灵活可控，易于调试 | 需要额外进程 |
| 系统Cron | 可靠 | 时间调整不便 |

**最终选择：独立定时服务**

优势：
- 可独立启停，不影响主服务
- 支持动态调整执行时间
- 方便调试和监控
- 可扩展为分布式调度

---

### 4.2 为什么采用智能知识积累？

**传统方案问题**

```
❌ 每天保存 → 知识库爆炸
❌ 手动筛选 → 工作量大
❌ 无去重 → 重复内容
```

**智能保存机制**

```python
# 1. AI价值评估
judge_result = llm.invoke(
    "判断内容是否值得保存：行业趋势/技术案例/用户洞察"
)

# 2. 相似度检测
similar_chunks = knowledge_client.search(
    query=content,
    min_score=0.85  # 相似度阈值
)

# 3. 自动去重
if similar_chunks:
    skip_save()  # 已有相似内容，跳过保存
```

**保留策略**

| 知识类型 | 保留期限 | 理由 |
|---------|---------|------|
| 行业趋势 | 180天 | 时效性强 |
| 技术案例 | 365天 | 长期价值 |
| 用户洞察 | 365天 | 需求相对稳定 |
| 项目经验 | 永久 | 经验宝贵 |
| 竞品分析 | 90天 | 动态易过时 |

---

### 4.3 为什么采用配置文件管理知识库？

**设计原则**

```
灵活性 > 简单性
配置 > 硬编码
```

**配置优先级**

```python
# 1. 环境变量（最高优先级，适合临时切换）
knowledge_table = os.getenv("KNOWLEDGE_TABLE_NAME")

# 2. 配置文件（适合长期配置）
if not knowledge_table:
    with open("data/knowledge_table.json") as f:
        knowledge_table = json.load(f)["table_name"]

# 3. 默认值（兜底）
if not knowledge_table:
    knowledge_table = "Car_Seat"
```

**优势**：
- 支持快速切换知识库
- 无需修改代码
- 适合多环境部署

---

## 五、最佳实践与经验总结

### 5.1 工作流设计原则

#### 原则1：节点职责单一

```
❌ 错误：一个节点做搜索+分析+推送
✅ 正确：搜索节点只做搜索，分析节点只做分析
```

**好处**：
- 易于调试和测试
- 可独立优化
- 失败时可快速定位

---

#### 原则2：状态定义最小化

```python
# ❌ 错误：节点使用全局状态
def analysis_node(state: GlobalState):
    pass

# ✅ 正确：节点使用独立状态
class AnalysisInput(BaseModel):
    search_results: List[dict]
    knowledge_results: List[dict]

class AnalysisOutput(BaseModel):
    analysis_result: dict

def analysis_node(state: AnalysisInput) -> AnalysisOutput:
    pass
```

**好处**：
- 数据流向清晰
- 避免意外修改
- 符合工程规范

---

#### 原则3：错误处理要优雅

```python
# ❌ 错误：知识库检索失败导致整个流程中断
knowledge_results = knowledge_client.search(...)
return AnalysisOutput(knowledge_results=knowledge_results)

# ✅ 正确：检索失败不影响主流程
try:
    knowledge_results = knowledge_client.search(...)
except Exception as e:
    logger.error(f"知识库检索失败: {e}")
    knowledge_results = []  # 空列表，不影响后续流程

return AnalysisOutput(knowledge_results=knowledge_results)
```

---

### 5.2 定时服务最佳实践

#### 1. 日志记录

```python
# 同时输出到文件和控制台
logging.basicConfig(
    handlers=[
        logging.FileHandler('/tmp/scheduler.log'),
        logging.StreamHandler()
    ]
)
```

#### 2. 进程管理

```bash
# 记录PID
echo $PID > /var/run/scheduler.pid

# 检查进程
if ps -p $PID > /dev/null; then
    echo "服务正在运行"
fi
```

#### 3. 优雅退出

```python
# 捕获终止信号
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def signal_handler(signum, frame):
    scheduler.shutdown()
    sys.exit(0)
```

---

### 5.3 知识库管理最佳实践

#### 1. 定期清理

```bash
# 每周检查过期知识
python scripts/cleanup_knowledge.py

# 输出统计
总文档数: 7
过期文档: 2
需要清理: 是
```

#### 2. 去重策略

```python
# 相似度阈值
min_score = 0.85

# 检索相似内容
similar = knowledge_client.search(
    query=new_content,
    min_score=min_score
)

# 已有相似内容则跳过
if similar.chunks:
    logger.info("跳过保存：已有相似内容")
    return
```

#### 3. 质量控制

```python
# AI评估内容价值
value_score = llm.invoke(
    "评估内容的知识价值：0.0-1.0分"
)

# 只保存高质量内容
if value_score < 0.7:
    logger.info("跳过保存：内容质量不足")
    return
```

---

### 5.4 调试与监控最佳实践

#### 1. 完整的日志

```python
# 节点开始
logger.info(f"开始执行节点: {node_name}")

# 关键步骤
logger.info(f"搜索到 {len(results)} 条资讯")

# 异常处理
logger.error(f"节点执行失败: {error}", exc_info=True)

# 节点结束
logger.info(f"节点执行完成，耗时: {elapsed}s")
```

#### 2. 状态监控

```bash
# 查看服务状态
bash scripts/scheduler_status.sh

# 输出示例
进程状态: ✅ 正在运行
执行时间: 每天 08:30
下次执行: 2026-03-31 08:30:00
```

#### 3. 手动测试

```bash
# 手动触发工作流
curl -X POST http://localhost:5000/run

# 快速验证功能
```

---

## 六、项目成果

### 6.1 功能完成度

| 功能项 | 完成状态 | 说明 |
|-------|---------|------|
| 自动搜索资讯 | ✅ 100% | 20条/天，时间过滤 |
| 知识库检索 | ✅ 100% | 10条相关知识 |
| AI分析报告 | ✅ 100% | 趋势洞察+创新建议 |
| 飞书推送 | ✅ 100% | 每天8:30自动推送 |
| 智能保存 | ✅ 100% | 自动去重+价值评估 |
| 后台运行 | ✅ 100% | 关闭网页不停止 |

### 6.2 代码统计

```
总文件数: 20+
代码行数: 约3000行
节点数量: 5个
配置文件: 3个
脚本工具: 6个
文档数量: 7个
```

### 6.3 知识库积累

```
知识库: Car_Seat_20260330_152242
文档数: 持续增长
覆盖领域: 行业趋势、技术案例、用户洞察
```

---

## 七、后续优化建议

### 7.1 短期优化（1-2周）

1. **搜索优化**
   - [ ] 实现双阶段搜索（指定站点 → 全网）
   - [ ] 添加搜索来源统计
   - [ ] 在推送消息中标注来源站点

2. **知识库优化**
   - [ ] 实现定期清理脚本
   - [ ] 添加知识库容量监控
   - [ ] 实现知识过期告警

3. **监控优化**
   - [ ] 添加推送失败重试机制
   - [ ] 实现执行结果通知
   - [ ] 添加性能监控

---

### 7.2 中期优化（1-3个月）

1. **架构优化**
   - [ ] 迁移到systemd服务
   - [ ] 实现分布式调度
   - [ ] 添加任务队列

2. **功能增强**
   - [ ] 支持自定义推送时间
   - [ ] 支持多推送渠道
   - [ ] 支持内容订阅

3. **智能化升级**
   - [ ] 基于用户反馈优化内容
   - [ ] 实现个性化推荐
   - [ ] 添加趋势预测

---

### 7.3 长期规划（3-6个月）

1. **产品化**
   - [ ] 开发Web管理界面
   - [ ] 支持多用户配置
   - [ ] 提供API服务

2. **商业化**
   - [ ] 支持多行业模板
   - [ ] 提供SaaS服务
   - [ ] 支持私有化部署

---

## 八、技术栈总结

### 8.1 核心技术

| 技术 | 版本 | 用途 |
|-----|------|------|
| LangGraph | 1.0.2 | 工作流编排 |
| Python | 3.12 | 开发语言 |
| APScheduler | Latest | 定时调度 |
| FastAPI | Latest | HTTP服务 |
| Pydantic | Latest | 数据验证 |

### 8.2 AI能力

| 能力 | 模型 | 用途 |
|-----|------|------|
| LLM | 豆包 | 内容分析、价值判断 |
| Web Search | - | 资讯搜索 |
| Knowledge | - | 知识库存储与检索 |

### 8.3 集成服务

| 服务 | 用途 |
|-----|------|
| 飞书 | 消息推送 |
| 对象存储 | 文件存储 |
| 日志服务 | 日志管理 |

---

## 九、参考资料

### 9.1 项目文档

| 文档 | 路径 | 说明 |
|-----|------|------|
| 项目索引 | AGENTS.md | 项目结构索引 |
| 知识库策略 | docs/KNOWLEDGE_RETENTION_POLICY.md | 保留策略设计 |
| 搜索优化 | docs/SEARCH_OPTIMIZATION_PLAN.md | 搜索策略说明 |
| 后台运行 | docs/SCHEDULER_DAEMON_GUIDE.md | 定时服务配置 |

### 9.2 技术文档

- [LangGraph官方文档](https://python.langchain.com/docs/langgraph)
- [APScheduler文档](https://apscheduler.readthedocs.io/)
- [Pydantic文档](https://docs.pydantic.dev/)

### 9.3 工具脚本

| 脚本 | 用途 |
|-----|------|
| start_scheduler_daemon.sh | 后台启动定时服务 |
| scripts/stop_scheduler.sh | 停止服务 |
| scripts/scheduler_status.sh | 查看状态 |
| scripts/check_schedule.py | 检查配置 |
| scripts/cleanup_knowledge.py | 清理知识库 |

---

## 十、致谢

本项目在开发过程中参考了以下资源：

- LangGraph框架提供的强大工作流编排能力
- Coze平台提供的AI能力支持
- 飞书开放平台的API支持

---

## 附录：快速启动指南

### A. 环境准备

```bash
# 1. 克隆项目
git clone <repository_url>
cd <project_name>

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量（可选）
export SCHEDULE_HOUR="8"
export SCHEDULE_MINUTE="30"
export KNOWLEDGE_TABLE_NAME="Car_Seat"
```

### B. 启动服务

```bash
# 1. 启动工作流HTTP服务
python src/main.py -m http -p 5000 &

# 2. 启动定时调度服务（后台运行）
bash start_scheduler_daemon.sh

# 3. 查看状态
bash scripts/scheduler_status.sh
```

### C. 管理命令

```bash
# 查看实时日志
tail -f /tmp/seat_push_scheduler.log

# 手动触发
curl -X POST http://localhost:5000/run

# 停止服务
bash scripts/stop_scheduler.sh

# 检查配置
python scripts/check_schedule.py
```

---

**项目完成时间**：2026年3月30日

**项目状态**：✅ 已完成，生产环境可用

---

# 💡 PPT生成建议

## 推荐PPT结构

### 第一部分：项目介绍（2-3页）
1. 封面：项目名称 + 时间
2. 项目背景与目标
3. 功能需求与技术选型

### 第二部分：技术架构（2-3页）
4. 整体架构图
5. 核心节点设计
6. 数据流转图

### 第三部分：问题与解决（5-6页）
7. 问题1：定时调度问题
8. 问题2：知识库删除限制
9. 问题3：搜索站点限制
10. 问题4：搜索时间过滤
11. 问题5：后台运行问题
12. 技术决策总结

### 第四部分：最佳实践（3-4页）
13. 工作流设计原则
14. 定时服务最佳实践
15. 知识库管理最佳实践
16. 调试与监控最佳实践

### 第五部分：成果与展望（2-3页）
17. 项目成果
18. 后续优化建议
19. 技术栈总结

### 第六部分：结束（1页）
20. 致谢 + Q&A

## PPT设计建议

- **配色**：使用科技蓝色系，体现专业性
- **图表**：多用流程图、架构图、对比表格
- **代码**：关键代码片段使用代码块展示
- **动画**：适度使用动画，突出重点内容

## 导入豆包/Kimi提示词

```
请根据以下Markdown文档内容生成一份专业的技术总结PPT：

[粘贴本文档内容]

要求：
1. 生成20页左右的PPT
2. 使用专业科技风格配色
3. 包含架构图、流程图、对比表格
4. 突出关键问题和解决方案
5. 适合技术分享和汇报场景
```
