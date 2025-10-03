"""
Classifier Agent - 分类代理
端口：8004
功能：内容分类

使用 Google A2A SDK 实现标准的 Agent-to-Agent 协议
"""
from a2a.server import A2AServer, create_app
from a2a.types import AgentCard, Skill, Message, Part, TextPart, DataPart, Role
import uvicorn
from datetime import datetime

# 分类关键词
CATEGORIES = {
    "AI": ["AI", "人工智能", "机器学习", "深度学习", "GPT", "模型", "OpenAI", "Gemini"],
    "科技": ["科技", "技术", "iPhone", "量子", "芯片", "苹果", "谷歌", "IBM"],
    "金融": ["金融", "比特币", "美联储", "利率", "股市", "投资", "美元"],
}


class ClassifierAgent(A2AServer):
    """分类 Agent - 使用 Google A2A SDK"""
    
    def __init__(self):
        # 创建 Agent Card
        agent_card = AgentCard(
            name="Classifier Agent",
            description="内容分类和标签识别智能代理",
            url="http://localhost:8004",
            version="1.0.0",
            capabilities={
                "streaming": False,
                "push_notifications": False
            },
            skills=[
                Skill(
                    id="classify",
                    name="分类",
                    description="对文本内容进行分类",
                    tags=["classification", "nlp", "categorization"],
                    examples=[
                        "对以下内容分类：...",
                        "识别文本类别：...",
                        "这段文字属于什么主题？"
                    ],
                    input_modes=["text/plain"],
                    output_modes=["text/plain", "application/json"]
                )
            ],
            default_input_modes=["text/plain"],
            default_output_modes=["text/plain", "application/json"]
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
        print(f"\n📨 收到分类请求")
        print(f"   Message ID: {message.message_id}")
        
        # 提取文本内容
        user_text = ""
        for part in message.parts:
            if isinstance(part.root, TextPart):
                user_text = part.root.text
                break
        
        print(f"📝 分类文本长度: {len(user_text)} 字符")
        
        # 执行分类
        category, confidence, scores = self._classify(user_text)
        
        print(f"✅ 分类结果: {category} (置信度: {confidence:.2f})")
        
        # 生成结果文本
        result_text = self._format_result(category, confidence, scores)
        
        # 创建响应消息
        response = Message(
            role=Role.AGENT,
            parts=[
                Part(root=TextPart(text=result_text)),
                Part(root=DataPart(data={"json": {
                    "category": category,
                    "confidence": confidence,
                    "scores": scores
                }}))
            ]
        )
        
        return response
    
    def _classify(self, text: str) -> tuple:
        """执行分类"""
        # 简单分类（基于关键词匹配）
        scores = {}
        for category, keywords in CATEGORIES.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                scores[category] = score
        
        # 确定类别
        if scores:
            category = max(scores, key=scores.get)
            confidence = scores[category] / len(CATEGORIES[category])
        else:
            category = "其他"
            confidence = 0.0
        
        return category, confidence, scores
    
    def _format_result(self, category: str, confidence: float, scores: dict) -> str:
        """格式化结果"""
        result = f"## 分类结果\n\n"
        result += f"**类别**: {category}\n"
        result += f"**置信度**: {confidence:.2%}\n\n"
        
        if scores:
            result += f"### 详细评分\n\n"
            for cat, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                result += f"- {cat}: {score} 个关键词匹配\n"
        
        return result

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 Classifier Agent 启动中...")
    print("="*60)
    print("📍 地址: http://localhost:8004")
    print("📋 功能: 内容分类")
    print("🔧 使用 Google A2A SDK")
    print("🔧 Agent Card: http://localhost:8004/.well-known/agent-card.json")
    print("="*60 + "\n")
    
    # 创建 Agent 实例
    agent = ClassifierAgent()
    
    # 使用 A2A SDK 创建 FastAPI app
    app = create_app(agent)
    
    # 启动服务器
    uvicorn.run(app, host="0.0.0.0", port=8004)
