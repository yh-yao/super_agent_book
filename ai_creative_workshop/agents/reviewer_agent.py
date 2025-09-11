from langchain import OpenAI, LLMChain, PromptTemplate

class ReviewerAgent:
    def __init__(self, model="gpt-4o-mini"):
        self.llm = OpenAI(model=model)
        self.template = PromptTemplate.from_template(
            "请检查以下文案是否简洁有力并符合年轻人风格。如果需要，请优化。\n\n文案: {text}"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.template)

    def run(self, text):
        return self.chain.run(text=text)
