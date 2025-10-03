"""
01 - 串行协作示例
Sequential Collaboration

工作流：
Collector → Summarizer → Translator

一个 Agent 的输出作为下一个 Agent 的输入
"""
import asyncio
from a2a.client import ClientFactory, create_text_message_object


async def main():
    print("\n" + "="*80)
    print("示例 1: 串行协作 - 新闻收集 → 摘要 → 翻译")
    print("="*80)
    
    # Agent 地址
    collector_url = "http://localhost:8001"
    summarizer_url = "http://localhost:8002"
    translator_url = "http://localhost:8003"
    
    try:
        # 步骤 1: 连接所有 Agent
        print("\n📡 步骤 1: 连接到所有 Agent...")
        
        collector = await ClientFactory.create_client(collector_url)
        print(f"  ✅ Collector Agent 已连接")
        
        summarizer = await ClientFactory.create_client(summarizer_url)
        print(f"  ✅ Summarizer Agent 已连接")
        
        translator = await ClientFactory.create_client(translator_url)
        print(f"  ✅ Translator Agent 已连接")
        
        # 步骤 2: 调用 Collector 收集新闻
        print("\n📰 步骤 2: 收集新闻...")
        topic = input("请输入新闻主题 (AI/科技/金融，默认: AI): ").strip() or "AI"
        
        collect_msg = create_text_message_object(f"收集关于 {topic} 的新闻，限制 3 条")
        
        news_data = ""
        async for event in collector.send_message(collect_msg):
            if hasattr(event, 'parts'):
                for part in event.parts:
                    if hasattr(part.root, 'text'):
                        news_data = part.root.text
        
        print(f"  ✅ 收集完成 ({len(news_data)} 字符)")
        print(f"\n  📄 新闻内容预览:")
        print("  " + "-"*76)
        print("  " + news_data[:200].replace("\n", "\n  ") + "...")
        print("  " + "-"*76)
        
        input("\n按 Enter 继续生成摘要...")
        
        # 步骤 3: 调用 Summarizer 生成摘要
        print("\n📝 步骤 3: 生成摘要...")
        summary_msg = create_text_message_object(f"对以下新闻生成摘要：\n\n{news_data}")
        
        summary = ""
        async for event in summarizer.send_message(summary_msg):
            if hasattr(event, 'parts'):
                for part in event.parts:
                    if hasattr(part.root, 'text'):
                        summary = part.root.text
        
        print(f"  ✅ 摘要完成 ({len(summary)} 字符)")
        print(f"\n  📄 摘要内容:")
        print("  " + "-"*76)
        print("  " + summary.replace("\n", "\n  "))
        print("  " + "-"*76)
        
        input("\n按 Enter 继续翻译...")
        
        # 步骤 4: 调用 Translator 翻译
        print("\n🌐 步骤 4: 翻译成英文...")
        translate_msg = create_text_message_object(f"将以下内容翻译成英文：\n\n{summary}")
        
        translation = ""
        async for event in translator.send_message(translate_msg):
            if hasattr(event, 'parts'):
                for part in event.parts:
                    if hasattr(part.root, 'text'):
                        translation = part.root.text
        
        print(f"  ✅ 翻译完成 ({len(translation)} 字符)")
        
        # 最终结果
        print("\n" + "="*80)
        print("🎉 串行协作完成！完整流程：")
        print("="*80)
        print(f"\n原始新闻 ({len(news_data)} 字符)")
        print("  ↓")
        print(f"中文摘要 ({len(summary)} 字符)")
        print("  ↓")
        print(f"英文翻译 ({len(translation)} 字符)")
        
        print("\n" + "="*80)
        print("📄 最终翻译结果:")
        print("="*80)
        print(translation)
        print("="*80)
        
    except ConnectionError as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n💡 请确保所有 Agent 服务都在运行:")
        print("   python agents/collector_agent.py")
        print("   python agents/summarizer_agent.py")
        print("   python agents/translator_agent.py")
    
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


def print_summary():
    """打印知识点总结"""
    print("\n📚 知识点总结")
    print("="*80)
    print("\n✅ 串行协作的特点:")
    print("   1. 顺序执行，一个接一个")
    print("   2. 后一个 Agent 依赖前一个的输出")
    print("   3. 总耗时 = 各Agent耗时之和")
    print("   4. 适合有明确依赖关系的任务")
    
    print("\n✅ 适用场景:")
    print("   - 数据处理管道（收集→清洗→分析）")
    print("   - 内容生产流水线（写作→编辑→发布）")
    print("   - 逐步加工转换（原文→摘要→翻译）")
    
    print("\n✅ 优点:")
    print("   - 逻辑清晰，易于理解")
    print("   - 错误易于定位")
    print("   - 实现简单")
    
    print("\n✅ 缺点:")
    print("   - 总耗时较长")
    print("   - 不能充分利用并发")
    print("   - 一个环节出错影响整体")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("\n🎓 这是一个教学示例")
    print("💡 学习如何让多个 Agent 串行协作\n")
    
    try:
        asyncio.run(main())
        print_summary()
        
        print("\n🎯 下一步")
        print("="*80)
        print("运行并行协作示例，学习如何提高效率:")
        print("  python clients/02_parallel.py")
        print("="*80 + "\n")
    
    except KeyboardInterrupt:
        print("\n\n👋 示例已取消")
