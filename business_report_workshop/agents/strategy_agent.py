from langchain import OpenAI, LLMChain, PromptTemplate

class StrategyAgent:
    def __init__(self):
        self.llm = OpenAI(model="gpt-4o-mini")
        self.prompt = PromptTemplate.from_template(
            "请基于以下数据特征与趋势图，撰写300字市场解读：{summary}"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def run(self, df_summary):
        return self.chain.run(summary=df_summary)
