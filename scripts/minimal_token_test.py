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

# 获取 token
token = os.getenv("COZE_API_KEY", "")
workspace_id = os.getenv("COZE_WORKSPACE_ID", "")

print(f"\n📋 环境变量：")
print(f"  COZE_API_KEY 长度: {len(token)}")
print(f"  COZE_WORKSPACE_ID: {workspace_id}")

if not token:
    print("\n❌ 错误：COZE_API_KEY 未设置")
    sys.exit(1)

print(f"\n📋 Token 详细信息：")
print(f"  前10字符: '{token[:10]}'")
print(f"  后10字符: '...{token[-10:]}'")
print(f"  repr(前20): {repr(token[:20])}")
print(f"  repr(后20): {repr(token[-20:])}")

# 检查 token 格式
if token.startswith("pat_"):
    print(f"  类型: ✅ 个人访问令牌 (pat_)")
elif token.startswith("sat_"):
    print(f"  类型: ✅ 服务访问令牌 (sat_)")
else:
    print(f"  类型: ⚠️ 未知，前缀: '{token[:4]}'")

# 检查特殊字符
print(f"\n📋 特殊字符检查：")
has_special = False
for i, c in enumerate(token[:30]):
    if ord(c) < 32 or ord(c) > 126:
        print(f"  ⚠️ 位置 {i}: 字符码 {ord(c)} (非法)")
        has_special = True
    
if not has_special:
    print(f"  ✅ 前30个字符无非法字符")

# 尝试调用搜索 API
print("\n" + "=" * 70)
print("📡 测试搜索 API")
print("=" * 70)

try:
    from coze_coding_dev_sdk import SearchClient
    from coze_coding_utils.runtime_ctx.context import new_context
    
    print(f"\n正在初始化客户端...")
    ctx = new_context("test")
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
    print(f"  错误信息: {error_msg[:300]}")
    
    # 特殊错误处理
    if "token" in error_msg.lower() and "segment" in error_msg.lower():
        print("\n" + "=" * 70)
        print("⚠️  Token 格式错误诊断")
        print("=" * 70)
        print("\n可能的原因：")
        print("  1. Token 在 GitHub Secrets 中被截断或修改")
        print("  2. Token 包含了隐藏的特殊字符（如不可见的空格）")
        print("  3. Token 值被错误地添加了引号")
        print("\n解决方案：")
        print("  1. 在 GitHub 仓库中删除 COZE_API_KEY secret")
        print("  2. 重新创建 secret，确保：")
        print("     - 完整复制 token（68个字符）")
        print("     - 直接粘贴，不要手动输入")
        print("     - 不要添加引号")
        print("     - 确保没有首尾空格")
        print(f"\n  3. 正确的 token 格式：")
        print(f"     pat_xxxxx... (68 字符)")
        print(f"     您的 token 长度: {len(token)} 字符")
        
        if len(token) != 68:
            print(f"     ⚠️ 长度不正确！期望 68 字符，实际 {len(token)} 字符")
    
    import traceback
    print(f"\n完整错误堆栈:")
    traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("❌ Token 验证失败")
    print("=" * 70)
    sys.exit(1)

