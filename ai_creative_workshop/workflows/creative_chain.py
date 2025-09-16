from agents.copywriter_agent import CopyWriterAgent
from agents.designer_agent import DesignerAgent
from agents.reviewer_agent import ReviewerAgent

class CreativeChain:
    def __init__(self):
        self.copywriter = CopyWriterAgent()
        self.designer = DesignerAgent()
        self.reviewer = ReviewerAgent()

    def run(self, product, audience):
        print(f"🚀 为产品 '{product}' 和目标受众 '{audience}' 生成创意广告..."  )
        # Step 1: 文案
        draft_text = self.copywriter.run(product, audience)
        print("📝 初稿文案:", draft_text)

        # Step 2: 校对
        final_text = self.reviewer.run(draft_text)
        print("✅ 最终文案:", final_text)

        # Step 3: 设计
        image_path = self.designer.run(f"广告海报：{final_text}，清凉夏日风格")
        print("🎨 生成海报:", image_path)

        return final_text, image_path
