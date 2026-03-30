"""
知识库重置工具 - 切换到新的知识库

由于SDK不支持删除API，采用创建新知识库的方式实现重置。
"""
import os
from coze_coding_dev_sdk import KnowledgeClient
from coze_coding_utils.runtime_ctx.context import new_context
from datetime import datetime


def reset_knowledge():
    """
    重置知识库（通过创建新知识库实现）
    """
    ctx = new_context(method="knowledge.reset")
    client = KnowledgeClient(ctx=ctx)
    
    # 当前知识库名称
    current_table = os.getenv("KNOWLEDGE_TABLE_NAME", "Car_Seat")
    
    # 生成新知识库名称（带时间戳）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    new_table = f"Car_Seat_{timestamp}"
    
    print(f"{'='*60}")
    print(f"知识库重置工具")
    print(f"{'='*60}\n")
    
    print(f"📊 当前知识库: {current_table}")
    print(f"🆕 新知识库: {new_table}")
    print()
    
    # 创建新知识库（通过添加一个初始文档来创建）
    print(f"正在创建新知识库...")
    
    init_doc = f"""【知识库初始化】汽车座椅产品规划知识库

创建时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
知识库版本: {timestamp}

说明:
本知识库用于存储汽车座椅产品规划相关的高价值内容，包括：
- 行业趋势报告
- 技术案例分析
- 用户需求洞察
- 项目经验总结
- 竞品分析报告

保留策略:
- 行业趋势：180天
- 技术案例：365天
- 用户洞察：365天
- 项目经验：永久保留
- 竞品分析：90天
"""
    
    try:
        from coze_coding_dev_sdk import KnowledgeDocument, DataSourceType
        
        docs = [
            KnowledgeDocument(
                source=DataSourceType.TEXT,
                raw_data=init_doc
            )
        ]
        
        response = client.add_documents(
            documents=docs,
            table_name=new_table
        )
        
        if response.code == 0:
            print(f"✅ 新知识库创建成功！")
            print(f"   Doc IDs: {response.doc_ids}")
            print()
            
            # 输出环境变量更新指令
            print(f"{'='*60}")
            print(f"⚠️  需要更新环境变量")
            print(f"{'='*60}\n")
            
            print(f"请在环境变量中设置：")
            print(f"export KNOWLEDGE_TABLE_NAME=\"{new_table}\"")
            print()
            
            print(f"或者在 .env 文件中添加：")
            print(f"KNOWLEDGE_TABLE_NAME={new_table}")
            print()
            
            print(f"或者修改配置文件：")
            print(f"data/knowledge_table.json:")
            print(f'{{"table_name": "{new_table}"}}')
            print()
            
            # 同时保存到本地配置
            import json
            config_path = "data/knowledge_table.json"
            os.makedirs("data", exist_ok=True)
            
            config_data = {
                "table_name": new_table,
                "created_at": datetime.now().isoformat(),
                "previous_table": current_table
            }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 配置已保存到: {config_path}")
            print()
            
            return new_table
        else:
            print(f"❌ 创建失败: {response.msg}")
            return None
            
    except Exception as e:
        print(f"❌ 创建异常: {str(e)}")
        return None
    
    finally:
        print(f"{'='*60}")
        print(f"重置完成")
        print(f"{'='*60}")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="知识库重置工具")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="实际执行重置（默认仅显示计划）"
    )
    
    args = parser.parse_args()
    
    if not args.execute:
        print(f"{'='*60}")
        print(f"知识库重置计划（模拟模式）")
        print(f"{'='*60}\n")
        
        current_table = os.getenv("KNOWLEDGE_TABLE_NAME", "Car_Seat")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_table = f"Car_Seat_{timestamp}"
        
        print(f"当前知识库: {current_table}")
        print(f"新知识库名: {new_table}")
        print()
        print(f"执行后将：")
        print(f"1. 创建新知识库: {new_table}")
        print(f"2. 生成配置文件: config/knowledge_config.json")
        print(f"3. 输出环境变量设置指令")
        print()
        print(f"⚠️  注意：旧知识库 {current_table} 的数据不会自动删除")
        print(f"   需要手动清理或联系管理员处理")
        print()
        print(f"如需实际执行，请使用: python {__file__} --execute")
        print(f"{'='*60}")
    else:
        reset_knowledge()


if __name__ == "__main__":
    main()
