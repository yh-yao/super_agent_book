"""
Collector Agent - 新闻收集代理 (教学最小版本)
端口：8001
功能：模拟从“数据库”收集新闻并返回文本 + 结构化数据
"""
import os
import uuid
import json
import re
from datetime import datetime

from dotenv import load_dotenv
from openai import OpenAI

from a2a.server.apps import A2AFastAPIApplication
from a2a.types import AgentCard, Message, Part, TextPart, DataPart, Role, AgentCapabilities, AgentSkill, MessageSendParams
from a2a.server.request_handlers import RequestHandler
import uvicorn

load_dotenv()

NEWS_DB = {
    "AI": [
        {"id": 1, "title": "OpenAI 发布 GPT-5", "content": "OpenAI 今天发布了最新的语言模型 GPT-5，在多项测试中表现优异。", "date": "2025-10-01"},
        {"id": 2, "title": "谷歌推出 Gemini 2.0", "content": "谷歌发布 Gemini 2.0 多模态模型，支持图像、视频、音频统一理解。", "date": "2025-10-02"},
        {"id": 3, "title": "AI 芯片市场增长迅猛", "content": "2025年全球AI芯片市场预计达到500亿美元。", "date": "2025-10-03"},
    ],
    "科技": [
        {"id": 4, "title": "苹果发布 iPhone 16", "content": "苹果秋季发布会推出 iPhone 16 系列。", "date": "2025-09-15"},
        {"id": 5, "title": "量子计算新进展", "content": "IBM 宣布实现 1000 量子比特的稳定运行。", "date": "2025-09-28"},
    ],
    "金融": [
        {"id": 6, "title": "比特币突破 10 万美元", "content": "比特币价格首次突破 10 万美元大关。", "date": "2025-10-01"},
        {"id": 7, "title": "美联储维持利率不变", "content": "美联储宣布维持基准利率在 5.5% 不变。", "date": "2025-09-20"},
    ]
}

class CollectorHandler:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    async def handle_message(self, message: Message) -> Message:
        # 1. 提取文本
        user_text = ""
        for part in message.parts:
            if isinstance(part.root, TextPart):
                user_text = part.root.text
                break
        print(f"[collector] 📨 收到请求: {user_text!r}")

        # 2. 解析请求（LLM -> fallback）
        topic, max_items = self._parse_request(user_text)
        print(f"[collector] 🔍 解析结果 topic={topic} max_items={max_items}")

        news_list = NEWS_DB.get(topic, NEWS_DB["AI"])[:max_items]

        # 3. 组织输出
        result = {
            "topic": topic,
            "count": len(news_list),
            "news": news_list,
            "timestamp": datetime.now().isoformat()
        }

        text_out = [f"收集到 {len(news_list)} 条关于 {topic} 的新闻：", ""]
        for i, n in enumerate(news_list, 1):
            text_out.append(f"{i}. {n['title']}\n   {n['content']}\n   日期: {n['date']}\n")
        result_text = "\n".join(text_out)

        # 4. 返回（补：message_id + role=agent）
        return Message(
            message_id=str(uuid.uuid4()),
            role=Role.agent,
            parts=[
                Part(root=TextPart(text=result_text)),
                Part(root=DataPart(data=result))
            ]
        )

    def _parse_request(self, text: str):
        try:
            available = list(NEWS_DB.keys())
            prompt = f"""解析用户新闻收集请求:
可选主题: {', '.join(available)}
用户输入: \"{text}\"
返回 JSON:
{{
  "topic": "主题 (默认 AI)",
  "max_items": 数量 (默认 3 最大 10)
}}"""
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个请求解析器，负责提取主题和数量"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            data = json.loads(resp.choices[0].message.content or "{}")
            topic = data.get("topic", "AI")
            if topic not in available:
                topic = "AI"
            max_items = min(int(data.get("max_items", 3)), 10)
            return topic, max_items
        except Exception as e:
            # 降级简单规则
            return self._extract_topic_simple(text), self._extract_count_simple(text)

    def _extract_topic_simple(self, text: str) -> str:
        for k in NEWS_DB:
            if k.lower() in text.lower():
                return k
        return "AI"

    def _extract_count_simple(self, text: str) -> int:
        nums = re.findall(r"\\d+", text)
        if nums:
            return min(int(nums[0]), 10)
        return 3

class CollectorRequestHandler(RequestHandler):
    """适配 A2A RequestHandler 接口，将 handle_message 暴露为 on_message_send"""
    def __init__(self, logic: CollectorHandler):
        self.logic = logic

    async def on_message_send(self, params: MessageSendParams, context=None):  # type: ignore[override]
        return await self.logic.handle_message(params.message)

    # 以下为协议要求的接口，当前示例不实现任务管理，统一返回 NotImplemented
    async def on_get_task(self, params, context=None):  # type: ignore[override]
        raise NotImplementedError
    async def on_cancel_task(self, params, context=None):  # type: ignore[override]
        raise NotImplementedError
    async def on_message_send_stream(self, params, context=None):  # type: ignore[override]
        raise NotImplementedError
    async def on_resubscribe_to_task(self, params, context=None):  # type: ignore[override]
        raise NotImplementedError
    async def on_set_task_push_notification_config(self, params, context=None):  # type: ignore[override]
        raise NotImplementedError
    async def on_get_task_push_notification_config(self, params, context=None):  # type: ignore[override]
        raise NotImplementedError
    async def on_list_task_push_notification_config(self, params, context=None):  # type: ignore[override]
        raise NotImplementedError
    async def on_delete_task_push_notification_config(self, params, context=None):  # type: ignore[override]
        raise NotImplementedError


if __name__ == "__main__":
    agent_card = AgentCard(
        name="Collector Agent",
        description="新闻收集智能代理",
        version="1.0.0",
        url="http://localhost:8001",
        capabilities=AgentCapabilities(streaming=False, push_notifications=False),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain", "application/json"],
        skills=[
            AgentSkill(
                id="collect_news",
                name="收集新闻",
                description="根据主题和数量收集新闻",
                tags=["news", "collection", "data"],
                examples=[
                    "收集关于 AI 的新闻，限制 3 条",
                    "获取科技新闻，最多 5 条",
                    "查找金融相关的新闻",
                ],
                input_modes=["text/plain"],
                output_modes=["application/json", "text/plain"],
            )
        ],
    )

    logic = CollectorHandler()
    handler = CollectorRequestHandler(logic)
    app_wrapper = A2AFastAPIApplication(agent_card, handler)
    # 通过 build() 获取真正的 FastAPI 实例
    fastapi_app = app_wrapper.build()
    print("[collector] ✅ FastAPI app 构建完成并绑定路由")
    print("🚀 Collector Agent 启动: http://localhost:8001")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8001)