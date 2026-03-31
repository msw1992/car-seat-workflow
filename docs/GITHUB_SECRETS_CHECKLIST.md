# 📋 GitHub Actions 环境变量配置清单

> 在 GitHub 部署前，请按此清单配置所有必需的环境变量

---

## 🔑 必需配置的 Secrets（5个）

访问路径：`GitHub仓库 → Settings → Secrets and variables → Actions → New repository secret`

### 1. COZE_API_KEY ⭐⭐⭐ 最关键

**名称：** `COZE_API_KEY`

**获取方式（详细步骤）：**

#### 步骤 1：访问 Coze 平台
- 国内用户：https://www.coze.cn
- 国际用户：https://www.coze.com

#### 步骤 2：进入个人设置
```
登录 → 点击右上角头像 → 选择「个人设置」
```

#### 步骤 3：创建 API Token
```
个人设置 → API Token → 创建新 Token
```

#### 步骤 4：设置权限（必须勾选）
- ✅ **搜索权限**（Search）
- ✅ **知识库读取权限**（Knowledge Read）
- ✅ **知识库写入权限**（Knowledge Write）
- ✅ **模型调用权限**（Model）

#### 步骤 5：复制 Token
⚠️ **重要：Token 只显示一次，请立即复制保存！**

**正确格式示例：**
```
pat_ABC123def456GHI789jkl012MNO345pqr678STU901vwx234
```

**格式说明：**
| 格式类型 | 示例 | 是否正确 |
|---------|------|---------|
| `pat_xxxxx` | `pat_ABC123def...` | ✅ 正确（个人访问令牌）|
| `sat_xxxxx` | `sat_ABC123def...` | ✅ 正确（服务访问令牌）|
| JWT 格式 | `eyJhbGciOi...` | ✅ 正确（JSON Web Token）|
| 无前缀 | `ABC123def...` | ❌ 错误 |
| 包含引号 | `"pat_xxxxx"` | ❌ 错误 |
| 包含空格 | `pat_xxxxx ` | ❌ 错误 |

**验证方法：**
```bash
# 方法 1：运行诊断脚本
export COZE_API_KEY="您的token"
python scripts/diagnose_token.py

# 方法 2：检查格式（本地）
echo "$COZE_API_KEY" | grep -E "^pat_|^sat_"
```

**⚠️ 常见错误：**
```
错误信息：token contains an invalid number of segments
原因：Token 格式不正确
解决：确保 token 以 pat_ 或 sat_ 开头，不包含引号、空格等字符
```

---

### 2. COZE_WORKLOAD_IDENTITY_API_KEY ⭐ 重要

**名称：** `COZE_WORKLOAD_IDENTITY_API_KEY`

**说明：**
- 这是 Coze SDK 的认证密钥
- **必须与 `COZE_API_KEY` 值完全相同**
- 如果您的 `COZE_API_KEY` 是 `pat_xxxxx`，这个也填 `pat_xxxxx`

**值：** 与 `COZE_API_KEY` 完全相同

**示例：**
```
COZE_API_KEY = pat_ABC123def456
COZE_WORKLOAD_IDENTITY_API_KEY = pat_ABC123def456  # 相同！
```

---

### 3. COZE_WORKSPACE_ID

**名称：** `COZE_WORKSPACE_ID`

**获取方式：**
1. 访问 Coze 平台
2. 打开工作空间
3. 从 URL 中获取 ID（例如：`https://www.coze.cn/workspace/123456`）

**格式示例：** `123456`

---

### 4. FEISHU_WEBHOOK_URL

**名称：** `FEISHU_WEBHOOK_URL`

**获取方式：**
1. 打开飞书群聊
2. 点击群设置 → 群机器人
3. 添加机器人 → 自定义机器人
4. 复制 Webhook 地址

**格式示例：** `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxx-xxxxx`

---

### 5. KNOWLEDGE_TABLE_NAME ⭐ 重要

**名称：** `KNOWLEDGE_TABLE_NAME`

**当前值：** `Car_Seat_20260330_152242`

**说明：**
- 这是您在 Coze 平台创建的知识库名称
- 工作流通过此名称访问知识库
- **注意：不是知识库ID，是名称**

**验证方式：**
```bash
# 本地运行测试脚本
python scripts/test_knowledge_access.py
```

---

## 🔧 自动配置的平台环境变量

以下环境变量已在 workflow 中自动配置，**无需手动设置**：

| 环境变量名称 | 值 | 说明 |
|------------|---|------|
| `COZE_INTEGRATION_BASE_URL` | `https://integration.coze.cn` | Coze 集成服务地址 |
| `COZE_INTEGRATION_MODEL_BASE_URL` | `https://integration.coze.cn/api/v3` | Coze 模型 API 地址 |
| `COZE_LOOP_BASE_URL` | `https://api.coze.cn` | Coze API 地址 |
| `COZE_OUTBOUND_AUTH_ENDPOINT` | `https://integration.coze.cn/api/v1/secret` | 认证端点 |
| `COZE_WORKLOAD_ACCESS_TOKEN_ENDPOINT` | `https://api.coze.cn/.well-known/token` | 访问令牌端点 |
| `COZE_WORKLOAD_IDENTITY_TOKEN_ENDPOINT` | `https://api.coze.cn/.well-known/token` | 身份令牌端点 |

这些是 Coze 平台的固定地址，已在 `.github/workflows/daily_push.yml` 中硬编码。

---

## 📸 配置示例

### 添加 Secret 的界面

```
┌─────────────────────────────────────────┐
│ Add secret                               │
├─────────────────────────────────────────┤
│                                          │
│ Name *                                   │
│ ┌─────────────────────────────────────┐ │
│ │ KNOWLEDGE_TABLE_NAME                │ │
│ └─────────────────────────────────────┘ │
│                                          │
│ Secret *                                 │
│ ┌─────────────────────────────────────┐ │
│ │ Car_Seat_20260330_152242            │ │
│ └─────────────────────────────────────┘ │
│                                          │
│              [Add secret]                │
└─────────────────────────────────────────┘
```

---

## ✅ 配置验证清单

配置完成后，请逐项确认：

- [ ] `COZE_API_KEY` 已添加
- [ ] `COZE_WORKSPACE_ID` 已添加
- [ ] `FEISHU_WEBHOOK_URL` 已添加
- [ ] `KNOWLEDGE_TABLE_NAME` 已添加（值为 `Car_Seat_20260330_152242`）
- [ ] 所有变量名拼写正确（区分大小写）
- [ ] 值没有多余空格

---

## 🧪 测试步骤

### 第1步：手动触发

```
Actions → daily_push → Run workflow → Run workflow
```

### 第2步：查看日志

期望看到：
```
✅ 从知识库 'Car_Seat_20260330_152242' 检索到 X 条相关知识
```

### 第3步：检查飞书

期望收到推送消息

---

## ⚠️ 常见错误

### 错误1：知识库未找到

**原因：** `KNOWLEDGE_TABLE_NAME` 配置错误

**解决：**
```bash
# 查看正确的知识库名称
cat data/knowledge_table.json
```

### 错误2：API认证失败

**原因：** `COZE_API_KEY` 错误或过期

**解决：** 在 Coze 平台重新生成 Token

### 错误3：飞书推送失败

**原因：** `FEISHU_WEBHOOK_URL` 错误

**解决：** 重新创建飞书机器人

---

## 📊 环境变量使用位置

| 环境变量 | 使用节点 | 用途 |
|---------|---------|------|
| `COZE_API_KEY` | 所有节点 | Coze API 认证 |
| `COZE_WORKSPACE_ID` | 工作流初始化 | 工作空间标识 |
| `KNOWLEDGE_TABLE_NAME` | knowledge_search_node | 知识库检索 |
| `FEISHU_WEBHOOK_URL` | feishu_push_node | 推送消息 |

---

## 💡 提示

1. **Secrets 是加密的**：配置后无法查看值，只能更新
2. **区分大小写**：变量名必须完全一致
3. **不要有空格**：复制值时注意去除首尾空格
4. **测试优先**：配置后先手动触发测试

---

## 🔗 相关文档

- [GitHub Actions 快速开始](../QUICKSTART_GITHUB_ACTIONS.md)
- [部署方案对比](../DEPLOYMENT_COMPARISON.md)
- [知识库管理指南](KNOWLEDGE_RESET_GUIDE.md)
