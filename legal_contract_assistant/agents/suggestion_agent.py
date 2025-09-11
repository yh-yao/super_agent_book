from langchain import OpenAI, LLMChain, PromptTemplate

class SuggestionAgent:
    def __init__(self):
        self.llm = OpenAI(model="gpt-4o-mini")
        self.prompt = PromptTemplate.from_template(
            "合同条款: {clause}\n相关法规: {laws}\n"
            "请给出合规修改建议，并引用相关条文。"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def run(self, clause, laws):
        return self.chain.run(clause=clause, laws="\n".join(laws))
