#!/usr/bin/env python3
"""
简化的索引构建测试脚本 - 用于诊断问题
"""

import os
import sys
from pathlib import Path

def test_corpus_loading():
    """测试语料库加载"""
    print("🧪 测试语料库加载...")
    
    sys.path.insert(0, str(Path(__file__).parent))
    
    try:
        from app.services.rag import _load_corpus
        docs = _load_corpus()
        
        print(f"✅ 成功加载 {len(docs)} 个文档块")
        if docs:
            print(f"📄 第一个文档示例:")
            doc = docs[0]
            print(f"   标题: {doc['title']}")
            print(f"   日期: {doc['date']}")
            print(f"   来源: {doc['url']}")
            print(f"   文本长度: {len(doc['text'])} 字符")
            print(f"   文本预览: {doc['text'][:100]}...")
        
        return docs
        
    except Exception as e:
        print(f"❌ 语料库加载失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_embedding_single():
    """测试单个文本的嵌入生成"""
    print("\n🧪 测试单个文本嵌入...")
    
    try:
        from app.services.llm import embed_texts
        
        test_text = "这是一个测试文本"
        print(f"🔤 测试文本: {test_text}")
        
        embeddings = embed_texts([test_text])
        
        if embeddings:
            print(f"✅ 嵌入生成成功")
            print(f"   维度: {len(embeddings[0])}")
            print(f"   前5个值: {embeddings[0][:5]}")
        else:
            print("❌ 嵌入为空")
            
        return True
        
    except Exception as e:
        print(f"❌ 嵌入生成失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment():
    """测试环境配置"""
    print("🧪 测试环境配置...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✅ API Key 已配置 (长度: {len(api_key)})")
        if api_key.startswith("sk-"):
            print("   格式正确")
        else:
            print("   ⚠️ 格式可能不正确")
    else:
        print("❌ API Key 未配置")
    
    model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    print(f"📊 嵌入模型: {model}")

def main():
    print("🔧 简化索引构建诊断工具")
    print("=" * 50)
    
    # 测试环境
    test_environment()
    
    # 测试语料库加载
    docs = test_corpus_loading()
    if not docs:
        return
    
    # 测试嵌入生成
    if not test_embedding_single():
        return
    
    print(f"\n🎯 诊断完成，基础功能正常")
    print("💡 如果基础功能正常，问题可能在于:")
    print("   1. 网络连接速度")
    print("   2. OpenAI API 限制")
    print("   3. 系统内存不足")

if __name__ == "__main__":
    main()