class GraderAgent:
    def run(self, answers, keys):
        results = []
        score = 0
        for a, k in zip(answers, keys):
            if a.strip() == k.strip():
                results.append("✔ 正确")
                score += 1
            else:
                results.append(f"✘ 错误，参考答案: {k}")
        return score, results
