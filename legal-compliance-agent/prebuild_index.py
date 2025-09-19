#!/usr/bin/env python3
"""
预构建向量索引脚本
使用方法: python prebuild_index.py
"""

import os
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("🚀 开始构建向量索引...")
    print("=" * 50)
    
    try:
        # 导入RAG服务
        from app.services import rag
        
        start_time = time.time()
        
        # 检查语料库
        corpus_files = list(Path("ingest/corpus").glob("*.*"))
        print(f"📂 发现 {len(corpus_files)} 个语料库文件:")
        for f in corpus_files:
            print(f"   - {f.name}")
        
        print("\n📊 开始处理文档和生成嵌入向量...")
        print("   (这可能需要1-3分钟，取决于网络速度)")
        
        # 构建或加载索引
        index, docs = rag.build_or_load()
        
        elapsed = time.time() - start_time
        
        print(f"\n✅ 索引构建完成！")
        print(f"📈 统计信息:")
        print(f"   - 处理文档块: {len(docs)}")
        print(f"   - 向量维度: {index.d}")
        print(f"   - 构建时间: {elapsed:.2f}秒")
        
        # 检查生成的文件
        vectorstore_dir = Path("vectorstore")
        if vectorstore_dir.exists():
            files = list(vectorstore_dir.glob("*"))
            print(f"   - 生成文件: {len(files)} 个")
            for f in files:
                size = f.stat().st_size / 1024  # KB
                print(f"     * {f.name} ({size:.1f} KB)")
        
        print(f"\n🎉 现在可以正常使用API了！")
        print(f"💡 测试命令:")
        print(f'   curl -X POST http://127.0.0.1:8000/api/qa \\')
        print(f'     -H "Content-Type: application/json" \\')
        print(f'     -d \'{{"question":"GDPR对处理记录有什么规定？","jurisdictions":["EU"]}}\'')
        
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        print("💡 请确保你在legal-compliance-agent目录下运行此脚本")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 构建失败: {e}")
        print(f"💡 请检查:")
        print(f"   - OpenAI API密钥是否正确设置")
        print(f"   - 网络连接是否正常")
        print(f"   - ingest/corpus/ 目录是否包含文档")
        sys.exit(1)

if __name__ == "__main__":
    main()