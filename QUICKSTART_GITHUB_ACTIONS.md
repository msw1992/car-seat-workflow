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
| `COZE_API_KEY` | `pat_xxxxx` | Coze平台 → 个人设置 → API Token |
| `COZE_WORKSPACE_ID` | `123456` | Coze平台工作空间ID |
| `FEISHU_WEBHOOK_URL` | `https://open.feishu.cn/xxx` | 飞书群 → 设置 → 群机器人 → 添加机器人 |
| `KNOWLEDGE_TABLE_NAME` | `Car_Seat_20260330_152242` | **知识库名称**（见下方说明） |

**⚠️ 重要说明：**

- `KNOWLEDGE_TABLE_NAME` 是您在 Coze 平台创建的知识库名称
- 当前知识库名称：`Car_Seat_20260330_152242`
- 可通过 `cat data/knowledge_table.json` 查看当前知识库配置
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
