from agents.retriever_agent import RetrieverAgent
from agents.generator_agent import GeneratorAgent
from agents.dialogue_agent import DialogueAgent

class HealthChain:
    def __init__(self):
        self.retriever = RetrieverAgent()
        self.generator = GeneratorAgent()
        self.dialogue = DialogueAgent()

    def run(self, query):
        docs = self.retriever.run(query)
        answer = self.generator.run(query, docs)
        return self.dialogue.run(answer)
