from langchain_openai import OpenAI
from langchain.prompts import PromptTemplate

class CopyWriterAgent:
    def __init__(self, model="gpt-4o-mini"):
        self.llm = OpenAI(model=model, temperature=0.7)
        self.template = PromptTemplate.from_template(
            "为产品'{product}'写一句针对{audience}的广告文案。要求：只输出一句话，不超过15个字，不要任何解释、符号或多个选项。"
        )
        self.chain = self.template | self.llm

    def run(self, product, audience):
        return self.chain.invoke({"product": product, "audience": audience})
