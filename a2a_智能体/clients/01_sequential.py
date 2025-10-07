"""
01 - 串行协作示例
Sequential Collaboration

工作流：
Collector → Summarizer → Translator

一个 Agent 的输出作为下一个 Agent 的输入
"""
import asyncio
import uuid
import httpx
from a2a.client.legacy import A2AClient
from a2a.types import (
    Message, Part, TextPart, Role,
    SendMessageRequest, MessageSendParams
)


async def main():
    print("\n" + "=" * 80)
    print("示例 1: 串行协作 - 新闻收集 → 摘要 → 翻译")
    print("=" * 80)

    collector_url = "http://localhost:8001"
    summarizer_url = "http://localhost:8002"
    translator_url = "http://localhost:8003"

    # 共享 httpx client
    # 增加超时时间，避免 LLM 调用阻塞导致 ReadTimeout
    httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))

    try:
        # 步骤 1: 连接所有 Agent（legacy 简单演示）
        print("\n📡 步骤 1: 连接到所有 Agent...")
        collector = A2AClient(httpx_client=httpx_client, url=collector_url)
        summarizer = A2AClient(httpx_client=httpx_client, url=summarizer_url)
        translator = A2AClient(httpx_client=httpx_client, url=translator_url)
        print("  ✅ 所有 Agent 已连接")

        # 步骤 2: 收集新闻
        print("\n📰 步骤 2: 收集新闻...")
        topic = input("请输入新闻主题 (AI/科技/金融，默认: AI): ").strip() or "AI"
        collect_message = Message(
            message_id=str(uuid.uuid4()),
            role=Role.user,
            parts=[Part(root=TextPart(text=f"收集关于 {topic} 的新闻，限制 3 条"))],
        )
        collect_req = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(message=collect_message)
        )
        collect_resp = await collector.send_message(collect_req)
        news_text = ""
        # collect_resp.root.result 里是 Task 或 Message，取其中的 message.parts
        result = getattr(collect_resp.root, 'result', None)
        if result and hasattr(result, 'message'):
            # Task 场景
            msg_obj = getattr(result, 'message')
        else:
            msg_obj = result or getattr(collect_resp, 'message', None)
        if msg_obj and hasattr(msg_obj, 'parts'):
            for part in msg_obj.parts:
                if hasattr(part.root, 'text'):
                    news_text = part.root.text
        print(f"  ✅ 收集完成 ({len(news_text)} 字符)")
        print("  " + "-" * 76)
        print(news_text[:300].replace("\n", "\n  ") + ("..." if len(news_text) > 300 else ""))
        print("  " + "-" * 76)

        input("\n按 Enter 继续生成摘要...")

        # 步骤 3: 摘要
        print("\n📝 步骤 3: 生成摘要...")
        summary_message = Message(
            message_id=str(uuid.uuid4()),
            role=Role.user,
            parts=[Part(root=TextPart(text=f"对以下新闻生成摘要：\n\n{news_text}"))],
        )
        summary_req = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(message=summary_message)
        )
        summary_resp = await summarizer.send_message(summary_req)
        summary_text = ""
        result = getattr(summary_resp.root, 'result', None)
        if result and hasattr(result, 'message'):
            msg_obj = getattr(result, 'message')
        else:
            msg_obj = result or getattr(summary_resp, 'message', None)
        if msg_obj and hasattr(msg_obj, 'parts'):
            for part in msg_obj.parts:
                if hasattr(part.root, 'text'):
                    summary_text = part.root.text
        print(f"  ✅ 摘要完成 ({len(summary_text)} 字符)")
        print("  " + "-" * 76)
        print(summary_text.replace("\n", "\n  "))
        print("  " + "-" * 76)

        input("\n按 Enter 继续翻译...")

        # 步骤 4: 翻译
        print("\n🌐 步骤 4: 翻译成英文...")
        translate_message = Message(
            message_id=str(uuid.uuid4()),
            role=Role.user,
            parts=[Part(root=TextPart(text=f"将以下内容翻译成英文：\n\n{summary_text}"))],
        )
        translate_req = SendMessageRequest(
            id=str(uuid.uuid4()),
            params=MessageSendParams(message=translate_message)
        )
        translate_resp = await translator.send_message(translate_req)
        translation_text = ""
        result = getattr(translate_resp.root, 'result', None)
        if result and hasattr(result, 'message'):
            msg_obj = getattr(result, 'message')
        else:
            msg_obj = result or getattr(translate_resp, 'message', None)
        if msg_obj and hasattr(msg_obj, 'parts'):
            for part in msg_obj.parts:
                if hasattr(part.root, 'text'):
                    translation_text = part.root.text

        print(f"  ✅ 翻译完成 ({len(translation_text)} 字符)")
        print("\n" + "=" * 80)
        print("🎉 串行协作完成！")
        print("=" * 80)
        print(translation_text)

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
    except KeyboardInterrupt:
        print("\n\n👋 示例已取消")
