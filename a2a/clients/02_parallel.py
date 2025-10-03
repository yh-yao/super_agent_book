"""
02 - 并行协作示例
Parallel Collaboration

工作流：
         → Collector (AI)
Start  → Collector (科技)  → Merge → Summarizer → End
         → Collector (金融)

多个 Agent 并行执行，提高效率
"""
import asyncio
from a2a.client import ClientFactory, create_text_message_object


async def main():
    print("\n" + "="*80)
    print("示例 2: 并行协作 - 多数据源并行收集")
    print("="*80)
    
    # Agent 地址
    collector_url = "http://localhost:8001"
    summarizer_url = "http://localhost:8002"
    
    try:
        # 步骤 1: 连接 Agent
        print("\n📡 步骤 1: 连接到 Agent...")
        
        collector = await ClientFactory.create_client(collector_url)
        print(f"  ✅ Collector Agent 已连接")
        
        summarizer = await ClientFactory.create_client(summarizer_url)
        print(f"  ✅ Summarizer Agent 已连接")
        
        # 步骤 2: 并行收集多个主题的新闻
        print("\n📰 步骤 2: 并行收集多个主题的新闻...")
        
        topics = ["AI", "科技", "金融"]
        print(f"  📝 主题列表: {', '.join(topics)}")
        
        # 创建所有请求
        tasks = []
        for topic in topics:
            msg = create_text_message_object(f"收集关于 {topic} 的新闻，限制 2 条")
            tasks.append(collector.send_message(msg))
        
        print(f"  🚀 启动 {len(tasks)} 个并行任务...")
        
        # 并行执行
        results = await asyncio.gather(*tasks)
        
        # 收集所有新闻文本
        all_news = []
        for i, (result, topic) in enumerate(zip(results, topics), 1):
            news_text = ""
            async for event in result:
                if hasattr(event, 'parts'):
                    for part in event.parts:
                        if hasattr(part.root, 'text'):
                            news_text = part.root.text
            
            all_news.append(news_text)
            print(f"  ✅ {topic} 新闻收集完成 ({len(news_text)} 字符)")
        
        # 合并所有新闻
        merged_news = "\n\n" + "="*60 + "\n\n".join(all_news)
        
        print(f"\n  📊 总计收集: {len(all_news)} 个主题, {len(merged_news)} 字符")
        
        input("\n按 Enter 继续生成统一摘要...")
        
        # 步骤 3: 生成统一摘要
        print("\n📝 步骤 3: 生成统一摘要...")
        
        summary_msg = create_text_message_object(
            f"对以下多主题新闻生成一个统一的摘要：\n\n{merged_news}"
        )
        
        summary = ""
        async for event in summarizer.send_message(summary_msg):
            if hasattr(event, 'parts'):
                for part in event.parts:
                    if hasattr(part.root, 'text'):
                        summary = part.root.text
        
        print(f"  ✅ 摘要完成 ({len(summary)} 字符)")
        
        # 最终结果
        print("\n" + "="*80)
        print("🎉 并行协作完成！")
        print("="*80)
        print(f"\n📊 性能对比:")
        print(f"  - 串行执行: 需要 {len(topics)} 次顺序调用")
        print(f"  - 并行执行: 所有任务同时进行")
        print(f"  - 时间节省: ~{(len(topics)-1)/len(topics)*100:.0f}%")
        
        print("\n" + "="*80)
        print("📄 多主题统一摘要:")
        print("="*80)
        print(summary)
        print("="*80)
        
    except ConnectionError as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n💡 请确保 Agent 服务正在运行")
    
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


def print_summary():
    """打印知识点总结"""
    print("\n📚 知识点总结")
    print("="*80)
    print("\n✅ 并行协作的特点:")
    print("   1. 多任务同时执行")
    print("   2. 显著提升效率")
    print("   3. 总耗时 ≈ 最慢的 Agent 耗时")
    print("   4. 适合独立无依赖的任务")
    
    print("\n✅ 适用场景:")
    print("   - 多数据源聚合")
    print("   - 批量数据处理")
    print("   - 多路径探索")
    print("   - 冗余备份策略")
    
    print("\n✅ 实现要点:")
    print("   - 使用 asyncio.gather()")
    print("   - 确保任务独立")
    print("   - 处理部分失败")
    print("   - 合理控制并发数")
    
    print("\n✅ 优点:")
    print("   - 大幅提升速度")
    print("   - 充分利用资源")
    print("   - 提高吞吐量")
    
    print("\n✅ 缺点:")
    print("   - 资源消耗较大")
    print("   - 需要并发控制")
    print("   - 错误处理复杂")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("\n🎓 这是一个教学示例")
    print("💡 学习如何让多个 Agent 并行协作\n")
    
    try:
        asyncio.run(main())
        print_summary()
        
        print("\n🎯 下一步")
        print("="*80)
        print("运行条件路由示例，学习智能选择:")
        print("  python clients/03_conditional.py")
        print("="*80 + "\n")
    
    except KeyboardInterrupt:
        print("\n\n👋 示例已取消")
