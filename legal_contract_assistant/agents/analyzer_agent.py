class AnalyzerAgent:
    def run(self, contract_text):
        risks = []
        if "违约责任" in contract_text:
            risks.append("违约责任条款需确认赔偿范围是否过高。")
        if "争议解决" not in contract_text:
            risks.append("缺少争议解决条款，建议增加仲裁/法院管辖。")
        return risks
