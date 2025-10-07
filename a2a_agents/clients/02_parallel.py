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
import uuid
import httpx
from a2a.client.legacy import A2AClient
from a2a.types import Message, Part, TextPart, Role, SendMessageRequest, MessageSendParams


def _build_text_message(text: str) -> SendMessageRequest:
    """构造发送请求 (与 01 示例保持一致)."""
    message = Message(
        message_id=str(uuid.uuid4()),
        role=Role.user,
        parts=[Part(root=TextPart(text=text))],
    )
    return SendMessageRequest(id=str(uuid.uuid4()), params=MessageSendParams(message=message))


async def _send_and_extract(client: A2AClient, req: SendMessageRequest) -> str:
    resp = await client.send_message(req)
    txt = ""
    result = getattr(resp.root, 'result', None)
    if result and hasattr(result, 'message'):
        msg_obj = getattr(result, 'message')
    else:
        msg_obj = result or getattr(resp, 'message', None)
    if msg_obj and hasattr(msg_obj, 'parts'):
        for part in msg_obj.parts:
            if hasattr(part.root, 'text'):
                txt = part.root.text
    return txt


async def _collect_topic(collector_client: A2AClient, topic: str, limit: int = 2) -> tuple[str, str]:
    req = _build_text_message(f"收集关于 {topic} 的新闻，限制 {limit} 条")
    text = await _send_and_extract(collector_client, req)
    return topic, text


async def main():
    print("\n" + "="*80)
    print("示例 2: 并行协作 - 多数据源并行收集")
    print("="*80)
    
    # Agent 地址
    collector_url = "http://localhost:8001"
    summarizer_url = "http://localhost:8002"
    httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
    
    try:
        # 步骤 1: 连接 Agent
        print("\n📡 步骤 1: 连接到 Agent...")
        collector = A2AClient(httpx_client=httpx_client, url=collector_url)
        summarizer = A2AClient(httpx_client=httpx_client, url=summarizer_url)
        print("  ✅ Collector / Summarizer Agent 已连接")

        # 步骤 2: 并行收集多个主题的新闻
        print("\n📰 步骤 2: 并行收集多个主题的新闻...")

        topics = ["AI", "科技", "金融"]
        print(f"  📝 主题列表: {', '.join(topics)}")

        # 创建所有并行任务 (注意: 此处真正并行消费事件流)
        tasks = [asyncio.create_task(_collect_topic(collector, topic)) for topic in topics]
        print(f"  🚀 启动 {len(tasks)} 个并行任务...")

        collected = await asyncio.gather(*tasks)

        all_news = []
        for topic, news_text in collected:
            all_news.append(news_text)
            print(f"  ✅ {topic} 新闻收集完成 ({len(news_text)} 字符)")

        # 合并所有新闻 (用显式分隔符连接)
        merged_news = ("\n\n" + "="*60 + "\n\n").join(all_news)

        print(f"\n  📊 总计收集: {len(all_news)} 个主题, {len(merged_news)} 字符")

        input("\n按 Enter 继续生成统一摘要...")

        # 步骤 3: 生成统一摘要
        print("\n📝 步骤 3: 生成统一摘要...")

        summary_req = _build_text_message(
            f"对以下多主题新闻生成一个统一的摘要：\n\n{merged_news}"
        )
        summary = await _send_and_extract(summarizer, summary_req)

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

    except Exception as e:  # noqa: BLE001
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await httpx_client.aclose()


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
