"""
Translator Agent - 翻译代理
端口：8003
功能：文本翻译

使用 Google A2A SDK 实现标准的 Agent-to-Agent 协议
"""
from a2a.server import A2AServer, create_app
from a2a.types import AgentCard, Skill, Message, Part, TextPart, Role
import uvicorn
from datetime import datetime

# 简单的翻译词典（实际应用中应使用翻译API）
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


class TranslatorAgent(A2AServer):
    """翻译 Agent - 使用 Google A2A SDK"""
    
    def __init__(self):
        # 创建 Agent Card
        agent_card = AgentCard(
            name="Translator Agent",
            description="多语言文本翻译智能代理",
            url="http://localhost:8003",
            version="1.0.0",
            capabilities={
                "streaming": False,
                "push_notifications": False
            },
            skills=[
                Skill(
                    id="translate",
                    name="翻译",
                    description="将文本翻译成指定语言",
                    tags=["translation", "nlp", "i18n"],
                    examples=[
                        "将以下内容翻译成英文：...",
                        "Translate to Chinese: ...",
                        "把这段话翻译成日语"
                    ],
                    input_modes=["text/plain"],
                    output_modes=["text/plain"]
                )
            ],
            default_input_modes=["text/plain"],
            default_output_modes=["text/plain"]
        )
        
        super().__init__(agent_card=agent_card)
    
    async def handle_message(self, message: Message) -> Message:
        """
        处理收到的 A2A 消息
        
        Args:
            message: 收到的消息对象
            
        Returns:
            Message: 响应消息
        """
        print(f"\n📨 收到翻译请求")
        print(f"   Message ID: {message.message_id}")
        
        # 提取文本内容
        user_text = ""
        for part in message.parts:
            if isinstance(part.root, TextPart):
                user_text = part.root.text
                break
        
        print(f"📝 翻译文本长度: {len(user_text)} 字符")
        
        # 执行翻译
        result = self._translate(user_text)
        
        print(f"✅ 翻译完成 ({len(result)} 字符)")
        
        # 创建响应消息
        response = Message(
            role=Role.AGENT,
            parts=[
                Part(root=TextPart(text=result))
            ]
        )
        
        return response
    
    def _translate(self, text: str) -> str:
        """执行翻译（简单的词汇替换演示）"""
        # 简单翻译（实际应调用翻译API）
        translated = text
        for chinese, english in TRANSLATIONS.items():
            translated = translated.replace(chinese, english)
        
        # 添加翻译说明
        result = "# Translation Result\n\n"
        result += "```\n"
        result += translated
        result += "\n```\n\n"
        result += "---\n"
        result += "*Note: This is a simulated translation for demonstration purposes.*\n"
        result += f"*In production, use translation APIs like Google Translate, DeepL, etc.*\n"
        
        return result

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Translator Agent 启动中...")
    print("="*60)
    print("📍 地址: http://localhost:8003")
    print("📋 功能: 文本翻译")
    print("🔧 使用 Google A2A SDK")
    print("🔧 Agent Card: http://localhost:8003/.well-known/agent-card.json")
    print("="*60 + "\n")
    
    # 创建 Agent 实例
    agent = TranslatorAgent()
    
    # 使用 A2A SDK 创建 FastAPI app
    app = create_app(agent)
    
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8003)
