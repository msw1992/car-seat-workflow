# 🔑 COZE_API_KEY 完整获取指南

> 这是最关键的配置步骤！请仔细阅读本文档。

---

## 📋 目录

- [什么是 COZE_API_KEY](#什么是-coze_api_key)
- [如何获取](#如何获取)
- [格式验证](#格式验证)
- [常见错误](#常见错误)
- [FAQ](#faq)

---

## 什么是 COZE_API_KEY

`COZE_API_KEY` 是您在 Coze 平台上的**个人访问令牌**（Personal Access Token），用于：

- ✅ 调用 Coze 搜索服务
- ✅ 访问和操作知识库
- ✅ 调用大语言模型

**重要：**
- 这是您个人的 Token，**不是**工作流部署的 Key
- Token 应该以 `pat_` 或 `sat_` 开头
- GitHub Actions 需要您提供自己的 Token 来调用 Coze 服务

---

## 如何获取

### 方法 1：从 Coze 平台创建（推荐）

#### 步骤 1：访问 Coze 平台

选择一个平台：
- **国内用户**：https://www.coze.cn
- **国际用户**：https://www.coze.com

#### 步骤 2：登录账号

如果没有账号，请先注册（免费）。

#### 步骤 3：进入个人设置

```
登录后 → 点击右上角头像 → 选择「个人设置」
```

#### 步骤 4：创建 API Token

```
个人设置页面 → API Token 标签页 → 点击「创建新 Token」
```

#### 步骤 5：设置 Token 名称和权限

**Token 名称：** 随意，建议使用 `github-actions-token`

**权限设置（必须勾选）：**
```
权限列表：
├─ ✅ 搜索（Search）
├─ ✅ 知识库读取（Knowledge Read）
├─ ✅ 知识库写入（Knowledge Write）
└─ ✅ 模型调用（Model）
```

⚠️ **如果不勾选这些权限，工作流将无法正常运行！**

#### 步骤 6：创建并复制

点击「创建」后，Token 会显示在页面上：

```
┌──────────────────────────────────────────────────────┐
│  Token 创建成功！                                      │
│                                                       │
│  pat_ABC123def456GHI789jkl012MNO345pqr678STU901...   │
│                                                       │
│  ⚠️ 请立即复制保存，关闭后将无法再次查看！              │
│                                                       │
│  [复制]  [关闭]                                        │
└──────────────────────────────────────────────────────┘
```

**立即点击「复制」！**

---

## 格式验证

### 正确格式示例

| 类型 | 格式 | 示例 |
|-----|------|------|
| 个人访问令牌 | `pat_xxxxx` | `pat_ABC123def456GHI789jkl012...` |
| 服务访问令牌 | `sat_xxxxx` | `sat_ABC123def456GHI789jkl012...` |
| JWT 格式 | `xxxx.yyyy.zzzz` | `eyJhbGciOiJIUzI1NiIsInR5cCI6...` |

### 验证方法

#### 方法 1：使用诊断脚本

```bash
# 设置环境变量
export COZE_API_KEY="您的token"

# 运行诊断
python scripts/diagnose_token.py
```

**正确输出：**
```
✅ Token 格式检查通过！
```

**错误输出：**
```
❌ 发现问题：
   1. token 格式应为 pat_xxxxx 或 sat_xxxxx
```

#### 方法 2：命令行检查

```bash
# Linux/macOS
echo "$COZE_API_KEY" | grep -E "^pat_|^sat_" && echo "✅ 格式正确" || echo "❌ 格式错误"

# 或直接查看前缀
echo "${COZE_API_KEY:0:4}"  # 应该输出 pat 或 sat_
```

---

## 常见错误

### 错误 1：Token 格式不正确

**错误信息：**
```
token contains an invalid number of segments
```

**原因：**
- Token 格式不对（缺少 `pat_` 或 `sat_` 前缀）
- Token 包含引号、空格等字符
- 复制不完整

**解决方法：**
```bash
# 1. 检查 Token 前缀
echo "$COZE_API_KEY" | head -c 10
# 应该输出：pat_xxxxx 或 sat_xxxxx

# 2. 检查是否包含引号
echo "$COZE_API_KEY" | grep -E '^"|^\''
# 如果有输出，说明包含引号，需要去除

# 3. 检查是否包含空格
echo "$COZE_API_KEY" | grep ' '
# 如果有输出，说明包含空格，需要去除
```

### 错误 2：Token 未配置

**错误信息：**
```
❌ 错误：COZE_API_KEY 未配置
```

**解决方法：**
1. 进入 GitHub 仓库
2. Settings → Secrets and variables → Actions
3. 点击「New repository secret」
4. Name: `COZE_API_KEY`
5. Secret: 粘贴您的 token
6. 点击「Add secret」

### 错误 3：Token 权限不足

**错误信息：**
```
no permission
```

**解决方法：**
1. 重新创建 Token
2. 确保勾选所有必需权限：
   - ✅ 搜索
   - ✅ 知识库读取
   - ✅ 知识库写入
   - ✅ 模型调用

### 错误 4：Token 过期或失效

**错误信息：**
```
authentication is invalid
```

**解决方法：**
1. 在 Coze 平台检查 Token 是否被撤销
2. 如果撤销了，重新创建新的 Token
3. 更新 GitHub Secrets

---

## FAQ

### Q1：Token 只显示一次，我忘了复制怎么办？

**A：** 需要重新创建新的 Token。旧的 Token 无法再次查看。

### Q2：我可以创建多个 Token 吗？

**A：** 可以。每个 Token 有独立的名称和权限，可以按需创建。

### Q3：Token 泄露了怎么办？

**A：** 立即在 Coze 平台撤销该 Token，然后创建新的：
```
个人设置 → API Token → 点击 Token 右侧的「撤销」按钮
```

### Q4：为什么 GitHub Actions 需要 Token？

**A：** GitHub Actions 运行在独立的服务器环境中，需要您的 Token 来调用 Coze 服务。沙箱环境中的 Token 只能在沙箱内使用。

### Q5：COZE_WORKLOAD_IDENTITY_API_KEY 和 COZE_API_KEY 有什么区别？

**A：** 在大多数情况下，它们的值应该**完全相同**。都是为了 Coze SDK 的认证。

### Q6：Token 有有效期吗？

**A：** Coze 个人访问令牌通常长期有效，除非您手动撤销。

### Q7：如何验证 Token 是否有效？

**A：** 运行诊断脚本：
```bash
export COZE_API_KEY="您的token"
python scripts/diagnose_token.py
```

---

## 📋 配置检查清单

配置前请确认：

- [ ] 已访问 Coze 平台并登录
- [ ] 已进入「个人设置 → API Token」
- [ ] 已创建新的 Token
- [ ] 已勾选所有必需权限（搜索、知识库、模型）
- [ ] 已复制完整的 Token（以 pat_ 或 sat_ 开头）
- [ ] 已在 GitHub Secrets 中添加 `COZE_API_KEY`
- [ ] 已在 GitHub Secrets 中添加 `COZE_WORKLOAD_IDENTITY_API_KEY`（值相同）
- [ ] 已运行诊断脚本验证格式

---

## 🔗 相关文档

- [GitHub Actions 快速开始](../QUICKSTART_GITHUB_ACTIONS.md)
- [GitHub Secrets 配置清单](GITHUB_SECRETS_CHECKLIST.md)
- [部署方案对比](../DEPLOYMENT_COMPARISON.md)
