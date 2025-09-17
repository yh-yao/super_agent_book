from typing import Dict, Tuple

from .improver import Improver
from .scorer import overall_score

from .llm_backend import OpenAIBackend


class SelfEvolvingAgent:
    """自进化商业报告生成代理。"""
    
    def __init__(self):
        self.improver = Improver()
        self.llm = OpenAIBackend()

    def _init_params(self) -> Dict:
        """初始化默认参数。"""
        params = {
            "bullet_prob": 0.55,
            "target_words": 800,  # 商业报告需要更多字数
            "temperature": 0.2
        }
        params["prefer_bullets"] = bool(
            params.get("bullet_prob", 0.55) >= 0.55
        )
        return params

    def _generate_report(self, prompt: str, params: Dict) -> str:
        """使用LLM后端生成报告。"""
        return self.llm.generate_report(prompt, params)

    def run(
        self, 
        source_text: str, 
        steps: int = 5, 
        target_score: float = 0.86,
        target_words: int = 800
    ) -> Tuple[str, Dict]:
        """运行自进化商业报告生成流程。"""
        params = self._init_params()
        # 使用传入的目标字数覆盖默认值
        params["target_words"] = target_words
        context = ""  # 上下文从空开始，通过搜索积累
        # 在提示词中明确指定目标字数
        prompt = f"{source_text}\n\n要求：请生成约{target_words}字的详细报告。"  # 用户输入的提示词
        draft = ''
        best_report, best_score = draft, {"total": -1.0}
        history = []

        print(f"\n🚀 开始自进化报告生成流程，目标：{steps}步，{target_words}字")
        print("=" * 60)

        for i in range(1, steps + 1):
            print(f"\n📍 步骤 {i}/{steps}")
            print("-" * 40)
            
            # 每次迭代都进行反思决策（搜索或修订）
            print("🤔 正在反思决策...")
            decision = self.llm.reflect_and_decide(
                prompt=prompt, context=context, draft=draft
            )
            
            if decision.get("action") == "search":
                query = decision.get("query", "")
                print(f"🔍 决定搜索：{query}")
                
                results = decision.get("results", [])
                print(f"📊 找到 {len(results)} 个搜索结果")
                
                snippets = " ".join([
                    r.get("snippet", "") for r in results 
                    if isinstance(r, dict)
                ])
                context += (
                    f"\n[搜索结果：{query}]\n"
                    f"{snippets}\n"
                )
                history.append({
                    "step": i, 
                    "action": "search", 
                    "query": query,
                    "search_results": results  # 保存完整的搜索结果
                })
                # 搜索后重新生成报告
                print("✍️  基于搜索结果重新生成报告...")
                full_context = f"{prompt}\n{context}" if context else prompt
                draft = self._generate_report(full_context, params)
            elif decision.get("action") == "revise" and draft:
                print("✏️  决定修订当前报告...")
                # 使用 LLM 的修订结果，不再重新生成
                draft = decision.get("new_text", draft)
            else:
                print("📝 生成初始报告...")
                # 如果是第一次迭代或其他情况，直接生成报告
                full_context = f"{prompt}\n{context}" if context else prompt
                draft = self._generate_report(full_context, params)

            # 再评估报告质量
            print("📊 评估报告质量...")
            evaluation_text = f"提示词：{source_text}\n生成的报告：{draft}"
            s = overall_score(
                evaluation_text, 
                draft, 
                target_words=target_words,
                prefer_bullets=bool(params.get("prefer_bullets", False))
            )
            
            print(f"📈 当前得分: {s['total']:.3f} (目标: {target_score})")
            print(f"   - 相关性: {s['relevance']:.3f}")
            print(f"   - 完整性: {s['completeness']:.3f}")
            print(f"   - 长度匹配: {s['length_fit']:.3f}")
            print(f"   - 结构: {s['structure']:.3f}")
            print(f"   - 冗余度: {s['redundancy']:.3f}")
            
            history.append({
                "step": i, 
                "action": "generate_and_score", 
                "score": s, 
                "summary": draft
            })
            
            if s["total"] > best_score["total"]:
                best_report, best_score = draft, s
                print(f"🎉 发现更好的报告！新最佳得分: {s['total']:.3f}")
                
            if s["total"] >= target_score:
                print(f"🏆 达到目标分数 {target_score}，提前结束！")
                break
                
            # 根据评估结果改进参数，为下一次迭代做准备
            print("🔧 根据评估结果调整参数...")
            params = self.improver.step(params, s)

        print(f"\n✅ 流程完成！最终最佳得分: {best_score['total']:.3f}")
        print("=" * 60)

        learned = {
            "bullet_prob": float(params.get("bullet_prob", 0.55)),
            "target_words": target_words
        }
        
        # 汇总所有搜索结果
        all_search_results = []
        for entry in history:
            if entry.get("action") == "search" and "search_results" in entry:
                all_search_results.append({
                    "step": entry["step"],
                    "query": entry["query"],
                    "results": entry["search_results"]
                })
        
        return best_report, {
            "best_score": best_score, 
            "history": history,
            "search_summary": all_search_results,
            "learned_params": learned
        }
