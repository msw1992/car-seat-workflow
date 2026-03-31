#!/usr/bin/env python3
"""测试用户提供的 token 是否有效"""
import os
import sys

# 设置用户提供的 token
test_token = "pat_tPcqlwBpsKl9cK2sEBUgOosDDKtqUSC9xDocEvrHL81Vspni8caW4WWF7R9HA3SL"

print("=" * 70)
print("🔍 Token 格式分析")
print("=" * 70)

print(f"\nToken: {test_token}")
print(f"长度: {len(test_token)} 字符")
print(f"前缀: {test_token[:4]}")

# 检查主体
body = test_token[4:]
print(f"主体: {body}")
print(f"主体长度: {len(body)} 字符")

# 检查是否包含点号（JWT格式）
if '.' in body:
    segments = body.split('.')
    print(f"\nJWT 段数: {len(segments)}")
    for i, seg in enumerate(segments, 1):
        print(f"  段{i} 长度: {len(seg)}")
else:
    print(f"\n非 JWT 格式（单段）")

# 检查特殊字符
special_chars = []
for i, c in enumerate(body):
    if not c.isalnum() and c not in '-_':
        special_chars.append((i, c))

if special_chars:
    print(f"\n⚠️ 发现特殊字符：")
    for pos, char in special_chars[:10]:
        print(f"  位置 {pos}: '{char}' (ASCII {ord(char)})")
else:
    print(f"\n✅ 无特殊字符")

# 尝试实际调用 API
print("\n" + "=" * 70)
print("🔬 尝试调用 Coze API")
print("=" * 70)

try:
    os.environ["COZE_API_KEY"] = test_token
    
    from coze_coding_dev_sdk import SearchClient
    from coze_coding_utils.runtime_ctx.context import new_context
    
    ctx = new_context("test")
    client = SearchClient(ctx=ctx)
    
    print("\n正在测试搜索 API...")
    try:
        response = client.search(
            query="test",
            search_type="web",
            count=1
        )
        print("✅ 搜索 API 调用成功！")
        if response.web_items:
            print(f"   返回 {len(response.web_items)} 条结果")
    except Exception as e:
        print(f"❌ 搜索 API 调用失败：")
        print(f"   错误类型: {type(e).__name__}")
        print(f"   错误信息: {str(e)[:200]}")
        
except ImportError as e:
    print(f"❌ 无法导入 SDK: {e}")
except Exception as e:
    print(f"❌ 发生错误: {e}")

print("\n" + "=" * 70)
