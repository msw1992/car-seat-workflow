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
print(f"  完整 token: {token}")
print(f"  长度: {len(token)} 字符")
print(f"  前10字符: '{token[:10]}'")
print(f"  后10字符: '...{token[-10:]}'")
print(f"  repr(完整): {repr(token)}")

# 检查 token 格式
if token.startswith("pat_"):
    print(f"  类型: ✅ 个人访问令牌 (pat_)")
    prefix = "pat_"
elif token.startswith("sat_"):
    print(f"  类型: ✅ 服务访问令牌 (sat_)")
    prefix = "sat_"
else:
    print(f"  类型: ⚠️ 未知，前缀: '{token[:4]}'")
    prefix = ""

# 检查主体部分
if prefix:
    body = token[len(prefix):]
    print(f"\n📋 Token 主体分析：")
    print(f"  主体: {body}")
    print(f"  主体长度: {len(body)} 字符")
    
    # 检查是否包含点号（JWT 格式）
    if '.' in body:
        segments = body.split('.')
        print(f"  JWT 格式: 是")
        print(f"  段数: {len(segments)}")
        for i, seg in enumerate(segments):
            print(f"    段{i+1} 长度: {len(seg)}")
            print(f"    段{i+1} 内容: {seg[:20]}...")
    else:
        print(f"  JWT 格式: 否（单段）")
        print(f"  ⚠️ Coze API 可能期望 JWT 格式的 token")

# 检查特殊字符
print(f"\n📋 特殊字符检查：")
has_special = False
for i, c in enumerate(token):
    if ord(c) < 32 or ord(c) > 126:
        print(f"  ⚠️ 位置 {i}: 字符码 {ord(c)} (非法字符)")
        has_special = True

if not has_special:
    print(f"  ✅ 所有字符都是可打印 ASCII 字符")

# 字节级检查
print(f"\n📋 字节级检查（前20字符）：")
for i in range(min(20, len(token))):
    c = token[i]
    print(f"  [{i}] '{c}' -> ord={ord(c)}, hex=0x{ord(c):02x}")

# 尝试调用搜索 API
print("\n" + "=" * 70)
print("📡 测试搜索 API")
print("=" * 70)

try:
    from coze_coding_dev_sdk import SearchClient
    from coze_coding_utils.runtime_ctx.context import new_context
    
    print(f"\n正在初始化客户端...")
    print(f"  COZE_INTEGRATION_BASE_URL: {os.getenv('COZE_INTEGRATION_BASE_URL', '未设置')}")
    print(f"  COZE_WORKSPACE_ID: {workspace_id}")
    
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
    print(f"  错误信息: {error_msg}")
    
    # 特殊错误处理
    if "token" in error_msg.lower() and "segment" in error_msg.lower():
        print("\n" + "=" * 70)
        print("⚠️  Token 格式错误诊断")
        print("=" * 70)
        print("\n🔍 Coze API 错误：token contains an invalid number of segments")
        print("\n可能的原因：")
        print("  1. Token 可能是旧版本的格式（非 JWT）")
        print("  2. Token 在 Coze 平台上需要特殊配置")
        print("  3. 您的账户可能需要特定权限")
        print("\n解决方案：")
        print("  1. 访问 https://www.coze.cn")
        print("  2. 个人设置 → API Token")
        print("  3. 删除旧的 token 并重新创建")
        print("  4. 确保勾选所有权限：")
        print("     ✅ 搜索（Search）")
        print("     ✅ 知识库读取（Knowledge Read）")
        print("     ✅ 知识库写入（Knowledge Write）")
        print("     ✅ 模型调用（Model）")
        print(f"\n  当前 token 信息：")
        print(f"    长度: {len(token)} 字符")
        print(f"    前缀: {prefix}")
        print(f"    主体格式: {'JWT (3段)' if '.' in body else '单段'}")
    
    import traceback
    print(f"\n完整错误堆栈:")
    traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("❌ Token 验证失败")
    print("=" * 70)
    sys.exit(1)

