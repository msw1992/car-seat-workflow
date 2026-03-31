#!/usr/bin/env python3
"""
Token 格式深度诊断工具
诊断 token 是否符合 Coze API 的格式要求
"""
import os
import sys
import re

def diagnose_token_format():
    """深度诊断 token 格式"""
    print("=" * 70)
    print("🔍 Coze API Token 格式深度诊断")
    print("=" * 70)
    
    # 获取 token
    token = os.getenv("COZE_API_KEY")
    
    if not token:
        print("\n❌ 错误：未找到 COZE_API_KEY 环境变量")
        return False
    
    print(f"\n📋 Token 基本信息：")
    print(f"   总长度: {len(token)} 字符")
    print(f"   前10字符: {token[:10] if len(token) >= 10 else token}")
    print(f"   后10字符: ...{token[-10:] if len(token) >= 10 else token}")
    
    # 检查 token 前缀
    issues = []
    
    # 检查 1: 前缀类型
    if token.startswith("pat_"):
        print(f"\n✅ Token 类型：个人访问令牌 (pat_)")
        token_type = "pat"
    elif token.startswith("sat_"):
        print(f"\n✅ Token 类型：服务访问令牌 (sat_)")
        token_type = "sat"
    else:
        print(f"\n⚠️  Token 类型：未知前缀")
        token_type = "unknown"
        issues.append("token 应以 pat_ 或 sat_ 开头")
    
    # 检查 2: 是否包含非法字符
    illegal_chars = []
    for i, char in enumerate(token):
        if ord(char) < 32 or ord(char) > 126:  # 非可打印ASCII字符
            illegal_chars.append((i, char, ord(char)))
    
    if illegal_chars:
        print(f"\n❌ 发现非法字符：")
        for pos, char, code in illegal_chars[:5]:  # 只显示前5个
            print(f"   位置 {pos}: 字符码 {code}")
        issues.append(f"token 包含 {len(illegal_chars)} 个非法字符")
    else:
        print(f"\n✅ 无非法字符")
    
    # 检查 3: 是否包含空白字符
    whitespace_chars = []
    for i, char in enumerate(token):
        if char in ' \t\n\r':
            whitespace_chars.append((i, char))
    
    if whitespace_chars:
        print(f"\n❌ 发现空白字符：")
        for pos, char in whitespace_chars:
            char_name = {' ': '空格', '\t': '制表符', '\n': '换行', '\r': '回车'}
            print(f"   位置 {pos}: {char_name.get(char, char)}")
        issues.append(f"token 包含 {len(whitespace_chars)} 个空白字符")
    else:
        print(f"\n✅ 无空白字符")
    
    # 检查 4: 是否以引号开头/结尾
    if token.startswith('"') or token.startswith("'"):
        print(f"\n❌ Token 以引号开头")
        issues.append("token 不应以引号开头")
    elif token.endswith('"') or token.endswith("'"):
        print(f"\n❌ Token 以引号结尾")
        issues.append("token 不应以引号结尾")
    else:
        print(f"\n✅ 无引号包裹")
    
    # 检查 5: Token 段数（针对 sat_ 和 pat_ 格式）
    if token_type in ["pat", "sat"]:
        # 去掉前缀后检查
        token_body = token[4:]  # 去掉 "pat_" 或 "sat_"
        
        print(f"\n📋 Token 主体信息：")
        print(f"   主体长度: {len(token_body)} 字符")
        
        # 检查是否包含点号（JWT 格式）
        if '.' in token_body:
            segments = token_body.split('.')
            print(f"   段数: {len(segments)} (包含点号分隔符)")
            
            if len(segments) == 3:
                print(f"   ✅ JWT 格式正确（3段）")
            else:
                print(f"   ⚠️  JWT 格式段数异常（期望3段）")
        else:
            print(f"   段数: 1 (无点号分隔符)")
            
            # 检查主体是否为有效的字符串
            if len(token_body) < 10:
                print(f"   ⚠️  主体长度过短")
                issues.append(f"token 主体长度仅 {len(token_body)} 字符")
            else:
                print(f"   ✅ 主体长度正常")
    
    # 检查 6: 尝试模拟 API 调用
    print(f"\n🔬 模拟 API 验证：")
    try:
        from coze_coding_dev_sdk import SearchClient
        from coze_coding_utils.runtime_ctx.context import new_context
        
        ctx = new_context("test")
        client = SearchClient(ctx=ctx)
        
        # 尝试一个简单的搜索
        print("   正在测试搜索API...")
        try:
            response = client.search(
                query="test",
                search_type="web",
                count=1
            )
            print("   ✅ API 调用成功！")
        except Exception as e:
            error_msg = str(e)
            print(f"   ❌ API 调用失败：{error_msg[:100]}")
            
            if "token" in error_msg.lower() or "segment" in error_msg.lower():
                issues.append(f"API 返回 token 错误: {error_msg[:100]}")
    except ImportError as e:
        print(f"   ⚠️  无法导入 SDK: {e}")
    
    # 总结
    print("\n" + "=" * 70)
    if issues:
        print("❌ 发现问题：")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print("\n📖 解决建议：")
        print("   1. 确认 token 是否完整复制（没有遗漏字符）")
        print("   2. 确认 token 没有包含引号、空格等字符")
        print("   3. 尝试重新生成 token")
        print("   4. 如果使用 sat_ token，确认是否有足够权限")
        print("\n   重新获取 token 步骤：")
        print("   → 访问 https://www.coze.cn")
        print("   → 个人设置 → API Token")
        print("   → 创建新 Token（勾选所有权限）")
        print("   → 立即复制并保存")
        
        return False
    else:
        print("✅ Token 格式检查通过！")
        print("\n如果仍然遇到问题，可能是：")
        print("   1. Token 权限不足（需要搜索、知识库、模型调用权限）")
        print("   2. Token 已过期或被撤销")
        print("   3. 服务 token (sat_) 和个人 token (pat_) 的权限不同")
        return True


if __name__ == "__main__":
    success = diagnose_token_format()
    sys.exit(0 if success else 1)
