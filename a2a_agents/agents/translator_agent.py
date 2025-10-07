"""
Translator Agent - 翻译代理
端口：8003
功能：文本翻译

使用 Google A2A SDK (0.3.8) 实现标准的 Agent-to-Agent 协议
使用 OpenAI GPT-4o-mini 进行智能翻译
"""
from a2a.server.apps import A2AFastAPIApplication
from a2a.types import AgentCard, Message, Part, TextPart, Role, AgentCapabilities, AgentSkill, MessageSendParams
from a2a.server.request_handlers import RequestHandler
import uvicorn
import os, uuid
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 简单的降级翻译词典
TRANSLATIONS = {
    "新闻": "news",
    "摘要": "summary",
    "收集": "collect",
    "生成": "generate",
    "关键词": "keywords",
    "主要内容": "main content",
    "统计": "statistics",
    "原文": "original text",
    "长度": "length",
    "字符": "characters",
    "压缩率": "compression ratio",
    "共": "total",
    "条": "items",
}


class TranslatorHandler:
    """翻译逻辑处理器"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    async def handle_message(self, message: Message) -> Message:
        # 提取用户文本
        user_text = ""
        for part in message.parts:
            if isinstance(part.root, TextPart):
                user_text = part.root.text
                break

        translation = self._translate(user_text)

        return Message(
            message_id=str(uuid.uuid4()),
            role=Role.agent,
            parts=[Part(root=TextPart(text=translation))]
        )

    def _translate(self, text: str) -> str:
        """使用 GPT-4o-mini 翻译，失败时用词典降级"""
        try:
            has_chinese = any("\u4e00" <= char <= "\u9fff" for char in text[:100])
            target_lang = "English" if has_chinese else "Chinese (Simplified)"

            prompt = f"""Please translate the following text to {target_lang}.

Requirements:
1. Keep the original meaning and tone
2. Preserve formatting (markdown, line breaks, etc.)
3. Use accepted translations for technical terms
4. Keep special symbols and numbers unchanged

Text:
{text}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional translator who provides accurate and natural translations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )

            translation = response.choices[0].message.content or ""
            result = f"# Translation Result ({self.model})\n\n**Target Language**: {target_lang}\n\n---\n\n{translation}\n\n---\n\n*Translated using OpenAI {self.model}*\n"
            return result

        except Exception as e:
            print(f"❌ GPT-4o-mini 翻译出错: {e}")
            translated = text
            for zh, en in TRANSLATIONS.items():
                translated = translated.replace(zh, en)

            return f"# Translation Result (Fallback)\n\n```\n{translated}\n```\n\n---\n*Note: Fallback translation used due to error.*\n"


class TranslatorRequestHandler(RequestHandler):
    def __init__(self, logic: TranslatorHandler):
        self.logic = logic

    async def on_message_send(self, params: MessageSendParams, context=None):  # type: ignore[override]
        return await self.logic.handle_message(params.message)

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
    # 定义 AgentCard
    agent_card = AgentCard(
        name="Translator Agent",
        description="多语言文本翻译智能代理",
        version="1.0.0",
        url="http://localhost:8003",
        capabilities=AgentCapabilities(streaming=False, push_notifications=False),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        skills=[
            AgentSkill(
                id="translate",
                name="翻译",
                description="将文本翻译成指定语言",
                tags=["translation", "nlp", "i18n"],
                examples=[
                    "将以下内容翻译成英文：...",
                    "Translate to Chinese: ...",
                    "把这段话翻译成日语",
                ],
                input_modes=["text/plain"],
                output_modes=["text/plain"],
            )
        ],
    )

    logic = TranslatorHandler()
    handler = TranslatorRequestHandler(logic)
    app_wrapper = A2AFastAPIApplication(agent_card, handler)
    fastapi_app = app_wrapper.build()
    print("[translator] ✅ FastAPI app 构建完成并绑定路由")
    print("🚀 Translator Agent 启动: http://localhost:8003")
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8003)
