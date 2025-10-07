"""
03 - 条件路由示例
Conditional Routing

工作流：
Classifier → [AI] → Specialized AI Handler
          → [科技] → Specialized Tech Handler  
          → [金融] → Specialized Finance Handler
          → [其他] → General Handler

根据内容分类，路由到不同的 Agent
"""
import asyncio
import uuid
import httpx
from a2a.client.legacy import A2AClient
from a2a.types import Message, Part, TextPart, Role, SendMessageRequest, MessageSendParams


def _build_text_message(text: str) -> SendMessageRequest:
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


async def _send_and_extract_classifier(client: A2AClient, req: SendMessageRequest) -> tuple[str, float, str]:
    resp = await client.send_message(req)
    category = "其他"
    confidence = 0.0
    detail_text = ""
    result = getattr(resp.root, 'result', None)
    if result and hasattr(result, 'message'):
        msg_obj = getattr(result, 'message')
    else:
        msg_obj = result or getattr(resp, 'message', None)
    if msg_obj and hasattr(msg_obj, 'parts'):
        for part in msg_obj.parts:
            root = getattr(part, 'root', None)
            if not root:
                continue
            if hasattr(root, 'data') and 'json' in root.data:
                data = root.data['json']
                category = data.get('category', category)
                confidence = data.get('confidence', confidence)
            elif hasattr(root, 'text'):
                detail_text = root.text
    return category, confidence, detail_text


async def main():
    print("\n" + "="*80)
    print("示例 3: 条件路由 - 基于分类的智能路由")
    print("="*80)
    
    # Agent 地址
    collector_url = "http://localhost:8001"
    classifier_url = "http://localhost:8004"
    summarizer_url = "http://localhost:8002"
    httpx_client = httpx.AsyncClient(timeout=httpx.Timeout(30.0))
    
    try:
        # 步骤 1: 连接 Agent
        print("\n📡 步骤 1: 连接到所有 Agent...")
        collector = A2AClient(httpx_client=httpx_client, url=collector_url)
        classifier = A2AClient(httpx_client=httpx_client, url=classifier_url)
        summarizer = A2AClient(httpx_client=httpx_client, url=summarizer_url)
        print("  ✅ 所有 Agent 已连接")

        # 步骤 2: 收集新闻
        print("\n📰 步骤 2: 收集新闻...")
        topic = input("请输入新闻主题 (AI/科技/金融，默认: 科技): ").strip() or "科技"
        collect_req = _build_text_message(f"收集关于 {topic} 的新闻，限制 3 条")
        news_data = await _send_and_extract(collector, collect_req)
        print(f"  ✅ 收集完成 ({len(news_data)} 字符)")

        input("\n按 Enter 继续分类...")

        # 步骤 3: 分类新闻
        print("\n🏷️  步骤 3: 对新闻进行分类...")
        classify_req = _build_text_message(f"对以下内容分类：\n\n{news_data}")
        category, confidence, detail_text = await _send_and_extract_classifier(classifier, classify_req)

        if detail_text:
            print(f"\n  📋 分类详情:")
            print("  " + "-"*76)
            print("  " + detail_text.replace("\n", "\n  "))
            print("  " + "-"*76)

        print(f"\n  🏷️  分类结果: {category}")
        print(f"  📊 置信度: {confidence:.2%}")

        input("\n按 Enter 继续路由...")

        # 步骤 4: 条件路由 - 根据分类决定处理方式
        print(f"\n🔀 步骤 4: 根据分类 [{category}] 路由到专门处理器...")
        if category == "AI":
            print("  ➡️  路由到: AI 专业摘要处理器")
            instruction = "作为 AI 专家，对以下 AI 新闻生成专业深度摘要，重点关注技术细节和行业影响"
        elif category == "科技":
            print("  ➡️  路由到: 科技专业摘要处理器")
            instruction = "作为科技分析师，对以下科技新闻生成专业摘要，重点关注产品特性和市场趋势"
        elif category == "金融":
            print("  ➡️  路由到: 金融专业摘要处理器")
            instruction = "作为金融分析师，对以下金融新闻生成专业摘要，重点关注市场影响和投资建议"
        else:
            print("  ➡️  路由到: 通用摘要处理器")
            instruction = "对以下新闻生成摘要"

        # 步骤 5: 执行专业化处理
        print(f"\n📝 步骤 5: 执行专业化摘要生成...")
        process_req = _build_text_message(f"{instruction}：\n\n{news_data}")
        result = await _send_and_extract(summarizer, process_req)
        print(f"  ✅ 处理完成 ({len(result)} 字符)")

        # 最终结果
        print("\n" + "="*80)
        print("🎉 条件路由协作完成！")
        print("="*80)
        print(f"\n📊 路由路径:")
        print(f"  收集 → 分类[{category}] → 专业处理器 → 结果")

        print("\n" + "="*80)
        print(f"📄 {category} 专业摘要:")
        print("="*80)
        print(result)
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
    print("\n✅ 条件路由的特点:")
    print("   1. 根据条件动态选择路径")
    print("   2. 实现专业化处理")
    print("   3. 提高处理质量")
    print("   4. 灵活的工作流")
    
    print("\n✅ 适用场景:")
    print("   - 智能客服系统")
    print("   - 内容分发平台")
    print("   - 多专家协作")
    print("   - 异常处理流程")
    
    print("\n✅ 实现要点:")
    print("   - 分类/判断逻辑")
    print("   - 路由规则设计")
    print("   - 专业化处理器")
    print("   - 降级策略")
    
    print("\n✅ 优点:")
    print("   - 专业化处理")
    print("   - 灵活可扩展")
    print("   - 提高准确性")
    print("   - 资源优化")
    
    print("\n✅ 缺点:")
    print("   - 需要分类器")
    print("   - 路由逻辑复杂")
    print("   - 维护成本高")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    print("\n🎓 这是一个教学示例")
    print("💡 学习如何基于条件路由到不同的 Agent\n")
    
    try:
        asyncio.run(main())
        print_summary()
        
        print("\n🎯 下一步")
        print("="*80)
        print("运行复杂管道示例，学习完整工作流:")
        print("  python clients/04_pipeline.py")
        print("="*80 + "\n")
    
    except KeyboardInterrupt:
        print("\n\n👋 示例已取消")
