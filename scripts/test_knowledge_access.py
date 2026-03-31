#!/usr/bin/env python3
"""
测试知识库访问是否正常
用于验证环境变量配置
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_knowledge_access():
    """测试知识库访问"""
    print("🔍 测试知识库访问...\n")
    
    # 检查环境变量
    required_vars = [
        "COZE_API_KEY",
        "COZE_WORKSPACE_ID",
        "KNOWLEDGE_TABLE_NAME"
    ]
    
    print("1️⃣ 检查环境变量：")
    all_set = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if len(value) > 10:
                display = value[:6] + "..." + value[-4:]
            else:
                display = "***"
            print(f"   ✅ {var}: {display}")
        else:
            print(f"   ❌ {var}: 未设置")
            all_set = False
    
    if not all_set:
        print("\n⚠️  请先配置环境变量")
        return False
    
    print("\n2️⃣ 测试知识库访问：")
    try:
        from coze_coding_dev_sdk import KnowledgeClient
        from coze_coding_utils.runtime_ctx.context import new_context
        
        # 创建上下文
        ctx = new_context(method="test")
        
        # 初始化客户端
        client = KnowledgeClient(ctx=ctx)
        
        # 获取知识库名称
        knowledge_table = os.getenv("KNOWLEDGE_TABLE_NAME")
        
        # 尝试检索
        response = client.search(
            query="汽车座椅",
            table_names=[knowledge_table],
            top_k=3,
            min_score=0.3
        )
        
        if response.code == 0:
            count = len(response.chunks) if response.chunks else 0
            print(f"   ✅ 知识库访问成功")
            print(f"   ✅ 知识库名称: {knowledge_table}")
            print(f"   ✅ 检索结果: {count} 条")
            
            if count > 0:
                print(f"\n   📚 前3条内容预览：")
                for i, chunk in enumerate(response.chunks[:3], 1):
                    content = chunk.content[:50] if chunk.content else ""
                    print(f"      {i}. {content}...")
            
            return True
        else:
            print(f"   ❌ 知识库访问失败: {response.msg}")
            return False
            
    except Exception as e:
        print(f"   ❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🧪 知识库访问测试")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    success = test_knowledge_access()
    
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    if success:
        print("✅ 测试通过，知识库可以正常访问")
    else:
        print("❌ 测试失败，请检查配置")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
