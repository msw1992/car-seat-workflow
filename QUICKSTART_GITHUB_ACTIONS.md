# ⚡ 快速开始：GitHub Actions 部署（10分钟完成）

> 最推荐的免费定时任务方案，无需服务器，零成本运行！

---

## 📋 前置条件

- ✅ GitHub 账号（免费）
- ✅ 项目代码已准备好

---

## 🚀 部署步骤

### 第1步：推送代码到 GitHub（2分钟）

#### 1.1 创建 GitHub 仓库

访问 [github.com/new](https://github.com/new) 创建新仓库：
- Repository name: `car-seat-workflow`
- 选择 **Private**（私有仓库）
- ❌ 不要勾选 "Add a README file"
- 点击 **Create repository**

#### 1.2 推送代码

```bash
# 在项目根目录执行

# 初始化 Git（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "feat: 初始化汽车座椅产品规划工作流"

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/car-seat-workflow.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

---

### 第2步：配置环境变量（3分钟）

#### 2.1 进入 Secrets 设置页面

```
GitHub仓库页面 → Settings → Secrets and variables → Actions
```

#### 2.2 添加以下 Secrets

点击 **New repository secret**，逐个添加：

| Secret名称 | 值 | 获取方式 |
|-----------|---|---------|
| `COZE_API_KEY` | `pat_xxxxx` | ⭐ **最关键！见下方详细说明** |
| `COZE_WORKLOAD_IDENTITY_API_KEY` | `pat_xxxxx` | **与 COZE_API_KEY 相同** |
| `COZE_WORKSPACE_ID` | `123456` | Coze平台工作空间ID |
| `FEISHU_WEBHOOK_URL` | `https://open.feishu.cn/xxx` | 飞书群 → 设置 → 群机器人 → 添加机器人 |
| `KNOWLEDGE_TABLE_NAME` | `Car_Seat_20260330_152242` | **知识库名称**（见下方说明） |

---

### 🔑 如何获取 COZE_API_KEY（最关键步骤）

**⚠️ 这是最容易出错的步骤！请仔细阅读：**

#### 方法 1：从 Coze 平台创建（推荐）

```
步骤 1：访问 Coze 平台
├─ 国内用户：https://www.coze.cn
└─ 国际用户：https://www.coze.com

步骤 2：进入个人设置
├─ 登录后，点击右上角头像
└─ 选择「个人设置」或「Personal Settings」

步骤 3：创建 API Token
├─ 选择「API Token」标签页
├─ 点击「创建新 Token」
├─ 设置 Token 名称（如：github-actions-token）
├─ ⚠️ 必须勾选以下权限：
│  ├─ ✅ 搜索（Search）
│  ├─ ✅ 知识库读取（Knowledge Read）
│  ├─ ✅ 知识库写入（Knowledge Write）
│  └─ ✅ 模型调用（Model）
├─ 点击「创建」
└─ ⚠️ 立即复制 token（关闭后无法再查看！）

步骤 4：验证 Token 格式
├─ 正确格式：pat_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
├─ 错误示例：
│  ├─ ❌ xxxxxxxxxxxxxxxxxxx（缺少 pat_ 前缀）
│  ├─ ❌ "pat_xxxxx"（包含引号）
│  ├─ ❌ pat_xxxxx\n（包含换行符）
│  └─ ❌ Bearer pat_xxxxx（包含 Bearer）
└─ 运行诊断脚本验证：python scripts/diagnose_token.py
```

#### Token 格式说明

| 格式 | 说明 | 示例 |
|-----|------|------|
| `pat_xxxxx` | 个人访问令牌 | ✅ 正确 |
| `sat_xxxxx` | 服务访问令牌 | ✅ 正确 |
| JWT格式 | 3段用.分隔 | ✅ 正确 |
| 其他格式 | 未知格式 | ❌ 错误 |

#### ⚠️ 常见错误

**错误信息：** `token contains an invalid number of segments`

**原因：** Token 格式不正确

**解决方法：**
1. 检查 token 是否以 `pat_` 或 `sat_` 开头
2. 确保 token 不包含引号、空格、换行符
3. 直接复制粘贴，不要手动输入

**验证命令：**
```bash
# 本地验证（需要先设置环境变量）
export COZE_API_KEY="您的token"
python scripts/diagnose_token.py
```

---

### 📋 其他 Secrets 获取方式

**COZE_WORKSPACE_ID：**
```
访问您的 Coze 工作空间
URL 格式：https://www.coze.cn/workspace/12345678
                                          ^^^^^^^^
                                          这就是 Workspace ID
```

**FEISHU_WEBHOOK_URL：**
```
飞书群 → 设置 → 群机器人 → 添加机器人 → 自定义机器人
↓
复制 Webhook 地址
```

**KNOWLEDGE_TABLE_NAME：**
```
值：Car_Seat_20260330_152242
（这是项目默认知识库名称，如果创建了新的请替换）
```

---

**⚠️ 重要说明：**

- `COZE_WORKLOAD_IDENTITY_API_KEY` **必须**与 `COZE_API_KEY` 值相同
- `KNOWLEDGE_TABLE_NAME` 是您在 Coze 平台创建的知识库名称
- 当前知识库名称：`Car_Seat_20260330_152242`
- 可通过 `cat data/knowledge_table.json` 查看当前知识库配置
- Coze 平台固定 URL 和 CozeLoop 追踪已在 workflow 中自动配置，无需手动设置
- **详细配置说明：** [docs/GITHUB_SECRETS_CHECKLIST.md](docs/GITHUB_SECRETS_CHECKLIST.md)

#### 配置示例截图

```
┌─────────────────────────────────────────┐
│ New secret                               │
├─────────────────────────────────────────┤
│ Name: COZE_API_KEY                       │
│ Secret: pat_xxxxxxxxxxxxxx               │
│                                          │
│ [Add secret]                             │
└─────────────────────────────────────────┘
```

---

### 第3步：启用 GitHub Actions（1分钟）

```
仓库页面 → Actions → I understand my workflows, go ahead and enable them
```

---

### 第4步：测试运行（2分钟）

#### 4.1 手动触发测试

```
Actions → daily_push → Run workflow → Run workflow
```

#### 4.2 查看执行日志

```
点击正在运行的任务 → 查看实时日志
```

预期输出：
```
✅ 工作流启动成功
✅ 搜索资讯完成
✅ 知识库检索完成
✅ AI分析完成
✅ 飞书推送成功
```

---

## ✅ 完成！

现在您的定时任务已经配置完成：

- ⏰ **执行时间**：每天北京时间 8:30
- 💰 **费用**：完全免费
- 📊 **月消耗**：约 150-300 分钟 << 2000 分钟免费额度
- 📝 **日志保存**：7天

---

## 🔧 常用操作

### 手动触发

```
Actions → daily_push → Run workflow
```

### 查看历史日志

```
Actions → 点击历史运行记录 → 查看详细日志
```

### 修改执行时间

编辑 `.github/workflows/daily_push.yml`：

```yaml
on:
  schedule:
    # cron: 分 时 日 月 周 (UTC时间)
    - cron: '30 0 * * *'  # 北京时间 8:30
```

时间对照表：

| 北京时间 | UTC时间 | cron表达式 |
|---------|---------|-----------|
| 08:30 | 00:30 | `30 0 * * *` |
| 09:00 | 01:00 | `0 1 * * *` |
| 18:00 | 10:00 | `0 10 * * *` |

### 停止定时任务

```
Settings → Actions → General → Actions permissions
选择 "Disable actions"
```

---

## ⚠️ 常见问题

### Q1: 提示 "No workflow files found"

**原因**：`.github/workflows/daily_push.yml` 文件未推送

**解决**：
```bash
git add .github/workflows/daily_push.yml
git commit -m "feat: 添加定时任务配置"
git push
```

### Q2: 执行失败，提示环境变量未找到

**原因**：Secrets 配置错误

**解决**：
1. 检查 Secret 名称是否完全一致（区分大小写）
2. 检查值是否正确（无多余空格）

### Q3: 时间不准确

**原因**：GitHub 使用 UTC 时间

**解决**：北京时间 = UTC + 8，调整 cron 表达式

### Q4: 想要多次执行

**解决**：添加多个 schedule：
```yaml
on:
  schedule:
    - cron: '30 0 * * *'   # 早上 8:30
    - cron: '0 10 * * *'   # 下午 18:00
```

---

## 📊 费用估算

| 项目 | 数量 |
|-----|------|
| 每天执行次数 | 1次 |
| 每次执行时长 | 5-10分钟 |
| 月执行次数 | 30次 |
| 月消耗分钟数 | 150-300分钟 |
| **免费额度** | **2000分钟/月** |
| **剩余额度** | **1700-1850分钟** |

---

## 🎉 下一步

部署成功后，您可以：

1. **监控执行**：每天查看 Actions 日志
2. **接收推送**：飞书群会收到每日资讯
3. **优化内容**：根据推送结果调整工作流
4. **扩展功能**：添加更多推送渠道（邮件、钉钉等）

---

## 📚 相关文档

- [免费部署方案对比](docs/FREE_DEPLOYMENT_GUIDE.md)
- [项目总结文档](docs/PROJECT_SUMMARY_FOR_PPT.md)
- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
