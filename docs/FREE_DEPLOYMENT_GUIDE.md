# 🆓 免费部署方案指南

本文档提供多种免费方案，让您的汽车座椅产品规划推送工作流实现长期定时运行。

---

## 方案一：GitHub Actions（最推荐）⭐⭐⭐⭐⭐

### 优势
- ✅ 完全免费：每月2000分钟额度
- ✅ 零服务器维护
- ✅ 代码更新自动部署
- ✅ 支持手动触发测试
- ✅ 执行日志自动保存

### 费用估算
- 每天1次 × 30天 = 30次执行
- 每次约5-10分钟
- 月消耗：150-300分钟 << 2000分钟免费额度

### 部署步骤

#### 第1步：推送代码到 GitHub

```bash
# 初始化 Git 仓库（如果还没有）
git init

# 添加远程仓库
git remote add origin https://github.com/YOUR_USERNAME/car-seat-workflow.git

# 提交代码
git add .
git commit -m "feat: 添加GitHub Actions定时任务"

# 推送到 GitHub
git push -u origin main
```

#### 第2步：配置 GitHub Secrets

进入 GitHub 仓库页面：
```
Settings → Secrets and variables → Actions → New repository secret
```

添加以下 Secrets：

| Secret名称 | 说明 | 示例 |
|-----------|------|------|
| `COZE_API_KEY` | Coze API密钥 | `pat_xxxxx` |
| `COZE_WORKSPACE_ID` | Coze工作空间ID | `123456` |
| `FEISHU_WEBHOOK_URL` | 飞书机器人Webhook | `https://open.feishu.cn/xxx` |
| `KNOWLEDGE_BASE_ID` | 知识库ID | `Car_Seat` |

#### 第3步：启用 GitHub Actions

```
仓库页面 → Actions → I understand my workflows, go ahead and enable them
```

#### 第4步：测试运行

```
Actions → daily_push → Run workflow → Run workflow
```

### 时间配置

当前配置为北京时间每天 8:30，如需修改：

```yaml
on:
  schedule:
    # cron 表达式：分 时 日 月 周 (UTC时间)
    # 北京时间 8:30 = UTC 0:30
    - cron: '30 0 * * *'
```

常用时间配置表：

| 北京时间 | UTC时间 | cron表达式 |
|---------|---------|-----------|
| 08:30 | 00:30 | `30 0 * * *` |
| 09:00 | 01:00 | `0 1 * * *` |
| 18:00 | 10:00 | `0 10 * * *` |

---

## 方案二：阿里云函数计算 ⭐⭐⭐⭐

### 优势
- ✅ 免费额度：每月100万次调用 + 40万GB-秒
- ✅ 无需管理服务器
- ✅ 按需付费，用多少付多少
- ✅ 支持定时触发器

### 费用估算
- 每天1次 × 30天 = 30次调用
- 每次执行约30秒
- 月消耗：30次调用 << 100万次免费额度

### 部署步骤

#### 第1步：开通阿里云函数计算

```
访问：https://fc.console.aliyun.com/
点击：立即开通（免费）
```

#### 第2步：创建服务和函数

```python
# 创建函数 index.py
import json
import subprocess
import sys

def handler(event, context):
    """函数入口"""
    # 安装依赖
    subprocess.check_call([sys.executable, "-m", "pip", "install", 
                          "-r", "requirements.txt", "-q"])
    
    # 执行工作流
    from src.main import main
    result = main(mode="once")
    
    return {
        "statusCode": 200,
        "body": json.dumps(result, ensure_ascii=False)
    }
```

#### 第3步：配置定时触发器

```
函数配置 → 触发器 → 创建触发器
- 触发器类型：定时触发器
- 名称：daily_push
- 触发方式：指定时间
- Cron表达式：0 30 8 * * * （每天8:30）
```

#### 第4步：配置环境变量

```
函数配置 → 环境变量
添加：
- COZE_API_KEY
- FEISHU_WEBHOOK_URL
- KNOWLEDGE_BASE_ID
```

### 详细教程
- [阿里云函数计算文档](https://help.aliyun.com/product/50980.html)
- [定时触发器配置](https://help.aliyun.com/document_detail/68172.html)

---

## 方案三：腾讯云函数 SCF ⭐⭐⭐⭐

### 优势
- ✅ 免费额度：每月100万次调用 + 40万GB-秒
- ✅ 与阿里云类似的功能
- ✅ 支持定时触发器

### 费用估算
与阿里云相同，远低于免费额度

### 部署步骤

#### 第1步：开通腾讯云 SCF

```
访问：https://console.cloud.tencent.com/scf
点击：立即开通（免费）
```

#### 第2步：创建函数

```python
# index.py
import json

def main_handler(event, context):
    """函数入口"""
    # 执行工作流
    from src.main import main
    result = main(mode="once")
    
    return {
        "statusCode": 200,
        "body": json.dumps(result, ensure_ascii=False)
    }
```

#### 第3步：配置定时触发器

```
触发器配置 → 创建触发器
- 触发方式：定时触发
- 触发周期：自定义触发周期
- Cron表达式：0 30 8 * * * *
```

---

## 方案四：PythonAnywhere（简单易用）⭐⭐⭐

### 优势
- ✅ 免费版支持每日定时任务
- ✅ 简单易用，适合Python项目
- ✅ 提供在线编辑器

### 限制
- ⚠️ 免费版只能设置1个定时任务
- ⚠️ 每天1次执行

### 部署步骤

#### 第1步：注册账号

```
访问：https://www.pythonanywhere.com/
注册免费账号
```

#### 第2步：上传代码

方式A：通过网页上传
```
Files → Upload a file → 选择项目zip文件
```

方式B：通过Git克隆
```bash
# 在 PythonAnywhere Bash 控制台
git clone https://github.com/YOUR_USERNAME/car-seat-workflow.git
```

#### 第3步：配置虚拟环境

```bash
# 在 Bash 控制台执行
cd car-seat-workflow
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 第4步：设置定时任务

```
Tasks → Schedule a new task
- Command: /home/YOUR_USERNAME/car-seat-workflow/venv/bin/python /home/YOUR_USERNAME/car-seat-workflow/src/main.py --mode once
- Hour: 8
- Minute: 30
```

---

## 方案五：Cron-job.org（外部触发）⭐⭐⭐

### 适用场景
适合配合现有服务使用，通过HTTP请求触发工作流

### 优势
- ✅ 完全免费
- ✅ 支持分钟级定时
- ✅ 无需编程

### 部署步骤

#### 第1步：部署工作流到云服务

将工作流部署到支持HTTP访问的服务：
- Vercel（免费）
- Render（免费）
- Railway（有免费额度）

#### 第2步：创建 HTTP 触发接口

```python
# 添加到 main.py
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/trigger', methods=['POST'])
def trigger_workflow():
    """HTTP 触发接口"""
    result = main(mode="once")
    return jsonify(result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
```

#### 第3步：配置 Cron-job.org

```
访问：https://cron-job.org/
注册账号 → Create cronjob
- URL: https://your-service.vercel.app/trigger
- Schedule: Daily at 08:30
- HTTP method: POST
```

---

## 方案对比总结

| 维度 | GitHub Actions | 阿里云FC | 腾讯云SCF | PythonAnywhere | Cron-job.org |
|-----|---------------|----------|-----------|----------------|--------------|
| **免费额度** | 2000分钟/月 | 100万次/月 | 100万次/月 | 1个任务 | 无限制 |
| **配置难度** | 简单 | 中等 | 中等 | 简单 | 简单 |
| **稳定性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **日志查看** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **手动触发** | ✅ | ✅ | ✅ | ❌ | ✅ |
| **执行时长** | 最长6小时 | 最长10分钟 | 最长24小时 | 最长5分钟 | 取决于服务 |
| **适合场景** | 通用 | 国内快速 | 国内快速 | 简单任务 | HTTP触发 |

---

## 🏆 最终推荐

### 推荐方案：GitHub Actions

**理由：**
1. ✅ 配置最简单（只需1个文件）
2. ✅ 免费额度最充足
3. ✅ 与Git集成，代码更新自动部署
4. ✅ 支持手动触发测试
5. ✅ 日志保存7天，便于调试

### 快速开始（GitHub Actions）

```bash
# 1. 推送代码到 GitHub
git add .
git commit -m "feat: 添加定时任务"
git push

# 2. 在 GitHub 网页配置 Secrets
Settings → Secrets → Actions → 添加环境变量

# 3. 启用 Actions
Actions → Enable workflows

# 4. 测试运行
Actions → Run workflow
```

**配置时间：约10分钟**

---

## 常见问题

### Q1: GitHub Actions 时间不对？
A: GitHub Actions 使用 UTC 时间，北京时间需要 -8 小时。
- 北京时间 8:30 = UTC 0:30 = `cron: '30 0 * * *'`

### Q2: 如何查看执行日志？
A: 
- GitHub Actions: Actions → 点击具体运行记录 → 查看日志
- 阿里云FC: 函数详情 → 调用日志
- 腾讯云SCF: 函数管理 → 调用日志

### Q3: 如何临时停止定时任务？
A:
- GitHub Actions: 仓库 Settings → Actions → 禁用
- 阿里云FC: 删除定时触发器
- 腾讯云SCF: 禁用触发器

### Q4: 执行失败如何告警？
A: 
- GitHub Actions: 配置失败通知邮件
- 云函数: 配置云监控告警

---

## 下一步

选择您喜欢的方案，按照对应步骤部署即可。推荐从 **GitHub Actions** 开始，最快10分钟即可完成部署！
