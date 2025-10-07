from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate

class ReviewerAgent:
    def __init__(self, model="gpt-4o-mini"):
        self.llm = OpenAI(model=model)
        self.template = PromptTemplate.from_template(
            "优化这个广告文案使其更适合年轻人：{text}\n\n只输出最终优化后的一句话，不超过15个字，不要解释过程。"
        )
        self.chain = self.template | self.llm

    def run(self, text):
        return self.chain.invoke({"text": text})
