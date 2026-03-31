#!/usr/bin/env python3
"""
Token 格式诊断工具
帮助用户检查 COZE_API_KEY 格式是否正确
"""
import os
import sys

def diagnose_token():
    """诊断 token 格式"""
    print("=" * 60)
    print("🔍 Coze API Token 格式诊断工具")
    print("=" * 60)
    
    # 检查环境变量
    token = os.getenv("COZE_API_KEY") or os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    
    if not token:
        print("\n❌ 错误：未找到 COZE_API_KEY 或 COZE_WORKLOAD_IDENTITY_API_KEY 环境变量")
        print("\n请检查：")
        print("1. GitHub Secrets 是否已配置 COZE_API_KEY")
        print("2. 本地环境是否已设置环境变量")
        return False
    
    print(f"\n📋 Token 信息：")
    print(f"   长度: {len(token)} 字符")
    print(f"   前缀: {token[:20]}..." if len(token) > 20 else f"   完整: {token}")
    
    # 检查 token 格式
    issues = []
    
    # 检查 1: 前缀格式
    if token.startswith("pat_"):
        print(f"\n✅ 前缀正确：个人访问令牌 (pat_)")
    elif token.startswith("sat_"):
        print(f"\n✅ 前缀正确：服务访问令牌 (sat_)")
    elif token.count(".") == 2 and len(token.split(".")) == 3:
        print(f"\n✅ 格式正确：JWT 格式")
    else:
        print(f"\n❌ 格式错误：未知的前缀")
        issues.append("token 格式应为 pat_xxxxx 或 sat_xxxxx 或 JWT 格式")
    
    # 检查 2: 段数
    if token.startswith("pat_") or token.startswith("sat_"):
        segments = token.split("_")
        if len(segments) >= 2:
            print(f"   段数: {len(segments)} (正确)")
        else:
            print(f"   段数: {len(segments)} (错误)")
            issues.append("token 应包含至少2个段（前缀_token值）")
    
    # 检查 3: 是否包含空格或特殊字符
    if " " in token or "\n" in token or "\t" in token:
        print(f"\n⚠️  警告：token 包含空白字符")
        issues.append("token 不应包含空格、换行符等")
    
    if token.startswith('"') or token.startswith("'"):
        print(f"\n⚠️  警告：token 以引号开头")
        issues.append("token 不应包含引号")
    
    # 总结
    print("\n" + "=" * 60)
    if issues:
        print("❌ 发现问题：")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        print("\n📖 正确的 token 格式示例：")
        print("   pat_ABC123def456GHI789jkl012MNO345pqr678")
        print("   sat_ABC123def456GHI789jkl012MNO345pqr678")
        print("\n获取方式：")
        print("1. 访问 https://www.coze.cn")
        print("2. 点击右上角头像 → 个人设置")
        print("3. 选择 'API Token' 标签页")
        print("4. 点击 '创建新 Token'")
        print("5. 勾选权限：搜索、知识库、模型调用")
        print("6. 创建并复制 token")
        return False
    else:
        print("✅ Token 格式检查通过！")
        return True


def show_github_secrets_guide():
    """显示 GitHub Secrets 配置指南"""
    print("\n" + "=" * 60)
    print("📖 GitHub Secrets 配置指南")
    print("=" * 60)
    
    print("""
步骤 1：获取 Coze API Token
├─ 访问：https://www.coze.cn
├─ 登录后点击右上角头像
├─ 选择「个人设置」
├─ 选择「API Token」标签页
├─ 点击「创建新 Token」
├─ 勾选权限：
│  ├─ ✅ 搜索（Search）
│  ├─ ✅ 知识库（Knowledge）
│  └─ ✅ 模型调用（Model）
├─ 点击「创建」
└─ ⚠️ 立即复制 token（只显示一次）

步骤 2：配置 GitHub Secrets
├─ 进入 GitHub 仓库
├─ Settings → Secrets and variables → Actions
├─ 点击「New repository secret」
├─ 添加以下 5 个 secrets：

Secret 名称                  值示例
─────────────────────────────────────────────────
COZE_API_KEY                pat_xxxxxxxxxxxxx
COZE_WORKLOAD_IDENTITY_API_KEY   pat_xxxxxxxxxxxxx (同上)
COZE_WORKSPACE_ID           12345678
FEISHU_WEBHOOK_URL          https://open.feishu.cn/open-apis/bot/v2/hook/xxx
KNOWLEDGE_TABLE_NAME        Car_Seat_20260330_152242

步骤 3：验证配置
├─ 进入 Actions 标签页
├─ 选择工作流
└─ 点击「Run workflow」手动触发测试
""")


if __name__ == "__main__":
    success = diagnose_token()
    
    if not success:
        show_github_secrets_guide()
        sys.exit(1)
    
    print("\n✅ 诊断完成，token 格式正确！")
    sys.exit(0)
