#!/usr/bin/env python3
"""
部署辅助脚本
用于验证环境配置是否正确
"""

import os
import sys

def check_environment():
    """检查环境变量是否配置完整"""
    required_vars = {
        "COZE_API_KEY": "Coze API密钥",
        "COZE_WORKSPACE_ID": "Coze工作空间ID",
        "FEISHU_WEBHOOK_URL": "飞书机器人Webhook地址",
        "KNOWLEDGE_BASE_ID": "知识库ID"
    }
    
    print("🔍 检查环境变量配置...\n")
    
    missing = []
    for var_name, description in required_vars.items():
        value = os.getenv(var_name)
        if value:
            # 部分隐藏敏感信息
            if len(value) > 10:
                display_value = value[:6] + "*" * (len(value) - 10) + value[-4:]
            else:
                display_value = "***"
            print(f"✅ {var_name}: {display_value}")
        else:
            print(f"❌ {var_name}: 未配置 ({description})")
            missing.append(var_name)
    
    print()
    if missing:
        print(f"⚠️  缺少 {len(missing)} 个必需的环境变量")
        print("\n请在 GitHub Secrets 中添加以下变量：")
        for var in missing:
            print(f"  - {var}")
        return False
    else:
        print("✅ 所有环境变量配置完整")
        return True

def test_workflow():
    """测试工作流是否可以正常运行"""
    print("\n🧪 测试工作流执行...\n")
    
    try:
        # 导入主函数
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from src.main import service
        import asyncio
        
        # 执行简单测试
        result = asyncio.run(service.run({"text": "测试执行"}))
        
        if result:
            print("✅ 工作流执行成功")
            return True
        else:
            print("⚠️  工作流执行返回空结果")
            return False
            
    except Exception as e:
        print(f"❌ 工作流执行失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 汽车座椅产品规划工作流 - 部署检查")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    
    # 检查环境变量
    env_ok = check_environment()
    
    # 测试工作流
    if env_ok and "--test" in sys.argv:
        workflow_ok = test_workflow()
        
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        if env_ok and workflow_ok:
            print("✅ 部署检查通过，可以开始定时任务")
        else:
            print("❌ 部署检查未通过，请检查配置")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
