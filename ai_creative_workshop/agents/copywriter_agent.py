from langchain import OpenAI, LLMChain, PromptTemplate

class CopyWriterAgent:
    def __init__(self, model="gpt-4o-mini"):
        self.llm = OpenAI(model=model, temperature=0.7)
        self.template = PromptTemplate.from_template(
            "请为{product}生成一句创意广告文案，目标受众是{audience}。"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.template)

    def run(self, product, audience):
        return self.chain.run(product=product, audience=audience)
