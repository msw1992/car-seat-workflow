#!/usr/bin/env python3
"""
最小化 Token 测试脚本
直接测试 token 是否有效，不依赖其他组件
"""
import os
import sys

print("=" * 70)
print("🔬 最小化 Token 测试")
print("=" * 70)

# 检查所有相关环境变量
print("\n📋 环境变量检查：")
env_vars = [
    'COZE_API_KEY',
    'COZE_WORKSPACE_ID', 
    'COZE_PROJECT_SPACE_ID',
    'COZE_INTEGRATION_BASE_URL',
    'COZE_WORKLOAD_IDENTITY_API_KEY',
]

for var in env_vars:
    value = os.getenv(var, '')
    if value:
        # 对于敏感信息，只显示部分
        if 'KEY' in var or 'TOKEN' in var:
            print(f"  {var}: {value[:20]}... (长度: {len(value)})")
        else:
            print(f"  {var}: {value}")
    else:
        print(f"  {var}: ❌ 未设置")

# 获取 token（SDK 使用 COZE_WORKLOAD_IDENTITY_API_KEY）
token = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY", "") or os.getenv("COZE_API_KEY", "")
workspace_id = os.getenv("COZE_PROJECT_SPACE_ID") or os.getenv("COZE_WORKSPACE_ID", "")

if not token:
    print("\n❌ 错误：COZE_WORKLOAD_IDENTITY_API_KEY (或 COZE_API_KEY) 未设置")
    sys.exit(1)

print(f"\n📋 使用的信息：")
print(f"  Token 长度: {len(token)} 字符")
print(f"  Workspace ID: {workspace_id}")

# 尝试调用搜索 API
print("\n" + "=" * 70)
print("📡 测试搜索 API")
print("=" * 70)

try:
    from coze_coding_dev_sdk import SearchClient
    from coze_coding_utils.runtime_ctx.context import new_context
    
    print(f"\n正在初始化客户端...")
    
    # 创建 context
    ctx = new_context("test")
    print(f"  Context.space_id: {ctx.space_id}")
    
    client = SearchClient(ctx=ctx)
    
    print(f"正在执行搜索...")
    response = client.search(
        query="汽车座椅",
        search_type="web",
        count=2
    )
    
    print(f"\n✅ 搜索成功！")
    if response.web_items:
        print(f"返回 {len(response.web_items)} 条结果")
        for i, item in enumerate(response.web_items[:2], 1):
            title = item.title[:50] if item.title else 'N/A'
            print(f"  {i}. {title}")
    else:
        print("无搜索结果（API 正常工作）")
    
    print("\n" + "=" * 70)
    print("✅ Token 验证成功！可以正常运行工作流")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ 搜索失败！")
    print(f"  错误类型: {type(e).__name__}")
    
    error_msg = str(e)
    print(f"  错误信息: {error_msg}")
    
    # 特殊错误处理
    if "workspace_id" in error_msg.lower():
        print("\n" + "=" * 70)
        print("⚠️  Workspace ID 问题")
        print("=" * 70)
        print("\n可能的原因：")
        print("  1. COZE_PROJECT_SPACE_ID 环境变量未设置")
        print("  2. GitHub Secrets 中的 COZE_WORKSPACE_ID 未配置")
        print("\n当前环境：")
        print(f"  COZE_PROJECT_SPACE_ID: {os.getenv('COZE_PROJECT_SPACE_ID', '未设置')}")
        print(f"  COZE_WORKSPACE_ID: {os.getenv('COZE_WORKSPACE_ID', '未设置')}")
        print(f"  Context.space_id: {ctx.space_id if 'ctx' in dir() else 'N/A'}")
        
    if "token" in error_msg.lower() and "segment" in error_msg.lower():
        print("\n" + "=" * 70)
        print("⚠️  Token 格式问题")
        print("=" * 70)
        print("\n您的 token 格式为单段（非 JWT）。")
        print("Coze API 可能需要特定格式的 token。")
        print("\n建议：")
        print("  1. 重新创建一个新的 token")
        print("  2. 确保勾选所有权限")
        print("  3. 确认使用的是正确的 token 类型")
    
    import traceback
    print(f"\n完整错误堆栈:")
    traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("❌ Token 验证失败")
    print("=" * 70)
    sys.exit(1)

