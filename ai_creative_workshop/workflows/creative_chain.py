from agents.copywriter_agent import CopyWriterAgent
from agents.designer_agent import DesignerAgent
from agents.reviewer_agent import ReviewerAgent

class CreativeChain:
    def __init__(self):
        self.copywriter = CopyWriterAgent()
        self.designer = DesignerAgent()
        self.reviewer = ReviewerAgent()

    def run(self, product, audience):
        # Step 1: 文案
        draft_text = self.copywriter.run(product, audience)

        # Step 2: 校对
        final_text = self.reviewer.run(draft_text)

        # Step 3: 设计
        image_path = self.designer.run(f"广告海报：{final_text}，清凉夏日风格")

        return final_text, image_path
