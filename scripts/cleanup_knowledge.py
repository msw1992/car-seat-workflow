"""
知识库清理工具 - 删除过期知识

注意：当前知识库SDK不支持删除API，此脚本仅作为未来功能的预留。
当前采用替代方案：在检索时过滤过期内容。
"""
import os
from datetime import datetime, timedelta
from typing import List
from coze_coding_dev_sdk import KnowledgeClient
from coze_coding_utils.runtime_ctx.context import new_context


# 知识保留策略（天数）
RETENTION_POLICY = {
    "行业趋势": 180,      # 6个月
    "技术案例": 365,      # 1年
    "用户洞察": 365,      # 1年
    "项目经验": -1,       # 永久保留
    "竞品分析": 90,       # 3个月
    "其他": 180           # 默认6个月
}


def parse_save_date(content: str) -> datetime:
    """从知识内容中解析保存时间"""
    import re
    # 匹配 "保存时间: 2026年03月30日" 格式
    match = re.search(r'保存时间:\s*(\d{4})年(\d{2})月(\d{2})日', content)
    if match:
        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
        return datetime(year, month, day)
    
    # 如果没有保存时间，返回当前时间（不删除）
    return datetime.now()


def parse_knowledge_type(content: str) -> str:
    """从知识内容中解析知识类型"""
    import re
    # 匹配 "知识类型: xxx" 或 "【xxx】" 格式
    match = re.search(r'知识类型:\s*([^\n]+)', content)
    if match:
        return match.group(1).strip()
    
    match = re.search(r'【([^】]+)】', content)
    if match:
        return match.group(1).strip()
    
    return "其他"


def calculate_expiry_date(save_date: datetime, knowledge_type: str) -> datetime:
    """计算过期日期"""
    retention_days = RETENTION_POLICY.get(knowledge_type, RETENTION_POLICY["其他"])
    
    if retention_days == -1:
        # 永久保留，返回一个远期日期
        return datetime.max
    else:
        return save_date + timedelta(days=retention_days)


def is_expired(content: str) -> tuple:
    """
    判断知识是否过期
    
    Returns:
        (is_expired: bool, reason: str, expiry_date: datetime)
    """
    save_date = parse_save_date(content)
    knowledge_type = parse_knowledge_type(content)
    expiry_date = calculate_expiry_date(save_date, knowledge_type)
    
    if expiry_date == datetime.max:
        return False, "永久保留", expiry_date
    
    is_expired = datetime.now() > expiry_date
    
    if is_expired:
        reason = f"已过期（保存于{save_date.strftime('%Y年%m月%d日')}，{knowledge_type}类型保留{RETENTION_POLICY[knowledge_type]}天）"
    else:
        remaining_days = (expiry_date - datetime.now()).days
        reason = f"未过期（剩余{remaining_days}天）"
    
    return is_expired, reason, expiry_date


def cleanup_knowledge(dry_run: bool = True):
    """
    清理过期知识
    
    Args:
        dry_run: 是否仅模拟运行（不实际删除）
    """
    ctx = new_context(method="knowledge.cleanup")
    client = KnowledgeClient(ctx=ctx)
    
    knowledge_table = os.getenv("KNOWLEDGE_TABLE_NAME", "Car_Seat")
    
    print(f"{'='*60}")
    print(f"知识库清理工具")
    print(f"知识库: {knowledge_table}")
    print(f"模式: {'模拟运行（仅检查）' if dry_run else '实际删除'}")
    print(f"{'='*60}\n")
    
    # 搜索所有知识（使用宽泛的查询词）
    # 注意：当前SDK不支持列出所有文档，这里使用多个宽泛查询来获取
    queries = ["汽车座椅", "趋势", "技术", "创新", "用户", "竞品"]
    
    all_docs = {}  # doc_id -> content
    all_chunks = []  # 所有chunk
    
    for query in queries:
        try:
            response = client.search(
                query=query,
                table_names=[knowledge_table],
                top_k=50  # 尽可能多获取
            )
            
            if response.code == 0 and response.chunks:
                for chunk in response.chunks:
                    if chunk.doc_id not in all_docs:
                        all_docs[chunk.doc_id] = chunk.content
                    all_chunks.append({
                        "doc_id": chunk.doc_id,
                        "chunk_id": chunk.chunk_id,
                        "content": chunk.content,
                        "score": chunk.score
                    })
        except Exception as e:
            print(f"⚠️  查询 '{query}' 失败: {str(e)}")
    
    print(f"📊 知识库统计：")
    print(f"   - 文档总数: {len(all_docs)}")
    print(f"   - 知识片段: {len(all_chunks)}")
    print()
    
    # 检查过期情况
    expired_docs = []
    active_docs = []
    
    for doc_id, content in all_docs.items():
        is_exp, reason, expiry_date = is_expired(content)
        
        if is_exp:
            expired_docs.append({
                "doc_id": doc_id,
                "reason": reason,
                "expiry_date": expiry_date
            })
        else:
            active_docs.append({
                "doc_id": doc_id,
                "reason": reason,
                "expiry_date": expiry_date
            })
    
    print(f"📋 过期检查结果：")
    print(f"   - 有效知识: {len(active_docs)}")
    print(f"   - 过期知识: {len(expired_docs)}")
    print()
    
    # 显示过期知识详情
    if expired_docs:
        print(f"❌ 以下知识已过期：")
        for i, doc in enumerate(expired_docs, 1):
            print(f"   {i}. Doc ID: {doc['doc_id']}")
            print(f"      原因: {doc['reason']}")
            print()
    
    # 显示有效知识概览
    if active_docs:
        print(f"✅ 以下知识有效：")
        for i, doc in enumerate(active_docs[:5], 1):  # 只显示前5个
            print(f"   {i}. Doc ID: {doc['doc_id']}")
            print(f"      状态: {doc['reason']}")
        
        if len(active_docs) > 5:
            print(f"   ... 还有 {len(active_docs) - 5} 个有效知识")
        print()
    
    # 执行删除（如果非模拟模式）
    if not dry_run and expired_docs:
        print(f"🗑️  正在删除过期知识...")
        
        # 注意：当前SDK不支持删除操作
        print(f"⚠️  警告：当前知识库SDK不支持删除API")
        print(f"   建议：")
        print(f"   1. 创建新的知识库")
        print(f"   2. 将有效知识迁移到新库")
        print(f"   3. 更新环境变量指向新库")
        
        # 预留删除代码（未来使用）
        # for doc in expired_docs:
        #     try:
        #         client.delete_document(doc_id=doc["doc_id"])
        #         print(f"   ✅ 已删除: {doc['doc_id']}")
        #     except Exception as e:
        #         print(f"   ❌ 删除失败 {doc['doc_id']}: {str(e)}")
    
    print(f"\n{'='*60}")
    print(f"清理完成")
    print(f"{'='*60}")
    
    return {
        "total_docs": len(all_docs),
        "total_chunks": len(all_chunks),
        "active_docs": len(active_docs),
        "expired_docs": len(expired_docs)
    }


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="知识库清理工具")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="实际执行删除（默认为模拟运行）"
    )
    
    args = parser.parse_args()
    
    # 执行清理
    stats = cleanup_knowledge(dry_run=not args.execute)
    
    # 输出统计
    print(f"\n📊 清理统计：")
    print(f"   总文档数: {stats['total_docs']}")
    print(f"   总片段数: {stats['total_chunks']}")
    print(f"   有效文档: {stats['active_docs']}")
    print(f"   过期文档: {stats['expired_docs']}")


if __name__ == "__main__":
    main()
