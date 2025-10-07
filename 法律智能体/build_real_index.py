#!/usr/bin/env python3
"""
构建真实语料库的向量索引
"""

import os
import sys
import time
from pathlib import Path

def build_real_index():
    """构建基于真实语料库的索引"""
    try:
        # 添加项目路径
        sys.path.insert(0, str(Path(__file__).parent))
        
        print("🚀 开始构建真实语料库索引...")
        print("=" * 50)
        
        # 检查语料库文件
        corpus_dir = Path("ingest/corpus")
        if not corpus_dir.exists():
            print("❌ 语料库目录不存在")
            return False
            
        corpus_files = list(corpus_dir.glob("*.*"))
        print(f"📂 发现 {len(corpus_files)} 个语料库文件:")
        for f in corpus_files:
            size = f.stat().st_size
            print(f"   - {f.name} ({size} bytes)")
        
        if not corpus_files:
            print("❌ 语料库目录为空")
            return False
        
        # 导入RAG服务并构建索引
        print("\n📊 开始处理文档...")
        
        from app.services import rag
        
        start_time = time.time()
        
        # 强制重新构建（删除现有索引）
        vectorstore_dir = Path("vectorstore")
        if vectorstore_dir.exists():
            print("🗑️  删除现有索引...")
            import shutil
            shutil.rmtree(vectorstore_dir)
        
        print("🔧 生成文档嵌入向量...")
        print("   (这可能需要1-2分钟，请耐心等待)")
        
        # 构建索引
        index, docs = rag.build_or_load()
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ 索引构建完成！")
        print(f"📈 统计信息:")
        print(f"   - 处理文档块: {len(docs)}")
        print(f"   - 向量维度: {index.d}")
        print(f"   - 构建时间: {elapsed:.2f}秒")
        
        # 显示文档样本
        print(f"\n📄 文档样本:")
        for i, doc in enumerate(docs[:3]):
            print(f"   {i+1}. {doc['title']} - {doc['chunk_id']}")
            print(f"      内容: {doc['text'][:100]}...")
        
        # 检查生成的文件
        if vectorstore_dir.exists():
            files = list(vectorstore_dir.glob("*"))
            print(f"\n💾 生成文件:")
            for f in files:
                size = f.stat().st_size / 1024  # KB
                print(f"   - {f.name} ({size:.1f} KB)")
        
        return True
        
    except Exception as e:
        print(f"❌ 构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_built_index():
    """测试构建的索引"""
    try:
        print(f"\n🧪 测试构建的索引...")
        
        from app.services import rag
        
        # 测试搜索
        test_queries = [
            "GDPR处理记录",
            "数据主体权利", 
            "CCPA消费者权利"
        ]
        
        for query in test_queries:
            print(f"\n🔍 搜索: '{query}'")
            hits = rag.search(query, k=2)
            
            if hits:
                print(f"   ✅ 找到 {len(hits)} 个相关结果")
                for i, hit in enumerate(hits):
                    score = hit.get('score', 0)
                    print(f"   {i+1}. {hit['title']} (相似度: {score:.3f})")
                    print(f"      内容: {hit['text'][:100]}...")
            else:
                print(f"   ❌ 未找到相关结果")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def main():
    print("🔧 真实语料库索引构建工具")
    print("=" * 50)
    
    # 构建索引
    if not build_real_index():
        print("\n❌ 索引构建失败")
        return
    
    # 测试索引
    if not test_built_index():
        print("\n❌ 索引测试失败")
        return
    
    print(f"\n🎉 索引构建并测试成功！")
    print(f"\n💡 现在可以正常使用API了:")
    print('curl -X POST http://127.0.0.1:8000/api/qa \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"question":"GDPR对处理记录有什么规定？","jurisdictions":["EU"]}\'')

if __name__ == "__main__":
    main()