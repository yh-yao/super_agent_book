"""
Collector Agent - 新闻收集代理
端口：8001
功能：模拟从数据库收集新闻

使用 Google A2A SDK 实现标准的 Agent-to-Agent 协议
"""
from a2a.server import A2AServer, create_app
from a2a.types import AgentCard, Skill, Message, Part, TextPart, DataPart, Role
import uvicorn
import json
from datetime import datetime
import re

# 模拟新闻数据库
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


class CollectorAgent(A2AServer):
    """新闻收集 Agent - 使用 Google A2A SDK"""
    
    def __init__(self):
        # 创建 Agent Card
        agent_card = AgentCard(
            name="News Collector Agent",
            description="收集各类新闻数据的智能代理",
            url="http://localhost:8001",
            version="1.0.0",
            capabilities={
                "streaming": False,
                "push_notifications": False
            },
            skills=[
                Skill(
                    id="collect_news",
                    name="收集新闻",
                    description="根据主题和数量收集新闻",
                    tags=["news", "collection", "data"],
                    examples=[
                        "收集关于 AI 的新闻，限制 3 条",
                        "获取科技新闻，最多 5 条",
                        "查找金融相关的新闻"
                    ],
                    input_modes=["text/plain"],
                    output_modes=["application/json", "text/plain"]
                )
            ],
            default_input_modes=["text/plain"],
            default_output_modes=["application/json", "text/plain"]
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
        print(f"   Role: {message.role}")
        
        # 提取文本内容
        user_text = ""
        for part in message.parts:
            if isinstance(part.root, TextPart):
                user_text = part.root.text
                break
        
        print(f"📝 用户请求: {user_text}")
        
        # 解析请求
        topic = self._extract_topic(user_text)
        max_items = self._extract_count(user_text)
        
        print(f"🔍 解析结果: topic={topic}, max_items={max_items}")
        
        # 获取新闻
        news_list = NEWS_DB.get(topic, NEWS_DB["AI"])[:max_items]
        
        # 格式化输出
        result = {
            "topic": topic,
            "count": len(news_list),
            "news": news_list,
            "timestamp": datetime.now().isoformat()
        }
        
        result_text = f"收集到 {len(news_list)} 条关于 {topic} 的新闻：\n\n"
        for i, news in enumerate(news_list, 1):
            result_text += f"{i}. {news['title']}\n"
            result_text += f"   {news['content']}\n"
            result_text += f"   日期: {news['date']}\n\n"
        
        print(f"✅ 返回 {len(news_list)} 条新闻")
        
        # 创建响应消息 - 使用 Google A2A 标准格式
        response = Message(
            role=Role.AGENT,
            parts=[
                Part(root=TextPart(text=result_text)),
                Part(root=DataPart(data={"json": result}))
            ]
        )
        
        return response
    
    def _extract_topic(self, text: str) -> str:
        """从文本中提取主题"""
        for keyword in NEWS_DB.keys():
            if keyword.lower() in text.lower():
                return keyword
        return "AI"  # 默认
    
    def _extract_count(self, text: str) -> int:
        """从文本中提取数量"""
        numbers = re.findall(r'\d+', text)
        if numbers:
            return min(int(numbers[0]), 10)  # 最多10条
        return 3  # 默认3条

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Collector Agent 启动中...")
    print("="*60)
    print("📍 地址: http://localhost:8001")
    print("📋 功能: 收集新闻数据")
    print("🔧 使用 Google A2A SDK")
    print("🔧 Agent Card: http://localhost:8001/.well-known/agent-card.json")
    print("="*60 + "\n")
    
    # 创建 Agent 实例
    agent = CollectorAgent()
    
    # 使用 A2A SDK 创建 FastAPI app
    app = create_app(agent)
    
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8001)
