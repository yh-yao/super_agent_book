from langchain import OpenAI, LLMChain, PromptTemplate

class GeneratorAgent:
    def __init__(self):
        self.llm = OpenAI(model="gpt-4o-mini")
        self.prompt = PromptTemplate.from_template(
            "根据以下医学资料，回答患者问题：{docs}\n\n问题：{query}\n\n"
            "请给出简要结论与解释说明，并以'仅供参考，请咨询医生'结尾。"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def run(self, query, docs):
        docs_text = "\n".join(docs)
        return self.chain.run(query=query, docs=docs_text)
