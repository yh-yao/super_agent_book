from agents.retriever_agent import RetrieverAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.suggestion_agent import SuggestionAgent

class ContractChain:
    def __init__(self):
        self.retriever = RetrieverAgent()
        self.analyzer = AnalyzerAgent()
        self.suggester = SuggestionAgent()

    def run(self, contract_text):
        risks = self.analyzer.run(contract_text)
        suggestions = []
        for clause in risks:
            laws = self.retriever.run(clause)
            suggestion = self.suggester.run(clause, laws)
            suggestions.append((clause, suggestion))
        return suggestions
