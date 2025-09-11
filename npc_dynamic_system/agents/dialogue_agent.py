from langchain import OpenAI, LLMChain, PromptTemplate

class DialogueAgent:
    def __init__(self):
        self.llm = OpenAI(model="gpt-4o-mini")
        self.prompt = PromptTemplate.from_template(
            "NPC角色背景：{background}\n记忆：{memory}\n玩家输入：{query}\n"
            "请生成符合角色设定的NPC对话。"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def run(self, query, background, memory):
        return self.chain.run(query=query, background=background, memory=memory)
