from langchain import OpenAI, LLMChain, PromptTemplate

class FeedbackAgent:
    def __init__(self):
        self.llm = OpenAI(model="gpt-4o-mini")
        self.prompt = PromptTemplate.from_template(
            "学生答题情况：{results}\n总分：{score}/{total}\n"
            "请根据错误知识点，给出学习建议（≤150字）。"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def run(self, results, score, total):
        return self.chain.run(results=results, score=score, total=total)
