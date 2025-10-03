"""
Summarizer Agent - 摘要生成代理
端口：8002
功能：生成文本摘要

使用 Google A2A SDK 实现标准的 Agent-to-Agent 协议
"""
from a2a.server import A2AServer, create_app
from a2a.types import AgentCard, Skill, Message, Part, TextPart, Role
import uvicorn
import json
from datetime import datetime


class SummarizerAgent(A2AServer):
    """摘要生成 Agent - 使用 Google A2A SDK"""
    
    def __init__(self):
        # 创建 Agent Card
        agent_card = AgentCard(
            name="Summarizer Agent",
            description="生成文本摘要和关键信息提取",
            url="http://localhost:8002",
            version="1.0.0",
            capabilities={
                "streaming": False,
                "push_notifications": False
            },
            skills=[
                Skill(
                    id="summarize",
                    name="生成摘要",
                    description="对长文本生成简洁摘要",
                    tags=["summarization", "nlp", "text-processing"],
                    examples=[
                        "对以下新闻生成摘要：...",
                        "提取关键信息：...",
                        "总结一下这篇文章"
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
        print(f"\n📨 收到消息")
        print(f"   Message ID: {message.message_id}")
        
        # 提取文本内容
        user_text = ""
        for part in message.parts:
            if isinstance(part.root, TextPart):
                user_text = part.root.text
                break
        
        print(f"📝 用户请求长度: {len(user_text)} 字符")
        
        # 生成摘要
        summary = self._generate_summary(user_text)
        
        print(f"✅ 生成摘要 ({len(summary)} 字符)")
        
        # 创建响应消息
        response = Message(
            role=Role.AGENT,
            parts=[
                Part(root=TextPart(text=summary))
            ]
        )
        
        return response
    
    def _generate_summary(self, text: str) -> str:
        """生成摘要"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # 提取标题行
        titles = [line for line in lines if any(c.isdigit() and '.' in line for c in line[:5])]
        
        # 生成摘要
        summary = "# 新闻摘要\n\n"
        summary += f"共收集到 {len(titles)} 条新闻\n\n"
        summary += "## 主要内容\n\n"
        
        for title in titles[:5]:  # 最多5条
            summary += f"- {title}\n"
        
        # 提取关键词
        keywords = ["AI", "科技", "发布", "突破", "增长", "OpenAI", "谷歌", "苹果", "比特币"]
        found_keywords = [kw for kw in keywords if kw in text]
        
        summary += f"\n## 关键词\n\n"
        summary += ", ".join(found_keywords) if found_keywords else "无"
        
        summary += f"\n\n## 统计\n\n"
        summary += f"- 原文长度: {len(text)} 字符\n"
        summary += f"- 摘要长度: {len(summary)} 字符\n"
        summary += f"- 压缩率: {len(summary)/len(text)*100:.1f}%\n"
        
        return summary

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Summarizer Agent 启动中...")
    print("="*60)
    print("📍 地址: http://localhost:8002")
    print("📋 功能: 生成文本摘要")
    print("🔧 使用 Google A2A SDK")
    print("🔧 Agent Card: http://localhost:8002/.well-known/agent-card.json")
    print("="*60 + "\n")
    
    # 创建 Agent 实例
    agent = SummarizerAgent()
    
    # 使用 A2A SDK 创建 FastAPI app
    app = create_app(agent)
    
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8002)
