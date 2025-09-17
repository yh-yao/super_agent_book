import json
import os
from datetime import datetime
from typing import Any, Dict

from openai import OpenAI

from .search import google_search_func, google_search_tool


class OpenAIBackend:
    """OpenAI后端，用于商业报告生成和反思。"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("缺少OPENAI_API_KEY")
        self.client = OpenAI()
        self.model = model

    def generate_report(self, prompt: str, style: Dict[str, Any]) -> str:
        """使用OpenAI API生成商业报告。"""
        prefer_bullets = style.get("prefer_bullets", False)
        target_words = int(style.get("target_words", 800))
        style_hint = "项目符号" if prefer_bullets else "段落"
        
        # 获取当前时间信息
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        system_prompt = (
            f"你是一个专业的商业分析师，专门生成高质量的商业报告。"
            f"当前时间是：{current_time}。在分析和搜索相关信息时，请考虑时间因素，"
            f"特别是寻找最新的新闻、数据和市场动态。"
            f"请根据用户的要求生成详细、专业的商业报告。"
        )
        
        user_prompt = (
            f"请基于以下要求生成一份详细的商业报告。\n\n"
            f"重要要求：\n"
            f"- 目标字数：约{target_words}字（这是关键要求，请务必达到）\n"
            f"- 格式：使用{style_hint}格式\n"
            f"- 内容要求：详细、专业、有深度\n\n"
            f"用户需求：\n{prompt}\n\n"
            f"请确保生成的报告内容丰富，达到约{target_words}字的要求。"
        )
        
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
        )
        content = resp.choices[0].message.content
        return content.strip() if content else ""

    def reflect_and_decide(self, prompt: str, context: str, draft: str):
        """对草稿进行反思并决定下一步行动。"""
        # 获取当前时间信息
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        system = (
            f"你是一个自进化的商业报告生成代理。当前时间是：{current_time}。"
            f"在搜索和分析时，请优先寻找最新的信息、新闻和数据。"
            f"你可以选择修订(REVISE)草稿或通过工具调用请求搜索(SEARCH)来收集缺失的信息。"
            f"返回你认为最佳的即时行动。"
        )
        
        user = f"""用户要求：
{prompt}

上下文信息（可能包含之前的搜索结果）：
{context}

当前草稿：
{draft}

指导原则：
- 如果信息缺失（例如市场规模、竞争格局、最新数据），请调用搜索工具获取具体的查询信息。特别关注最新的新闻和数据。
- 否则，请修订草稿以提高清晰度、覆盖面、简洁性和结构。
修订时返回修订后的文本。
"""
        
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            tools=[google_search_tool],  # type: ignore
            tool_choice="auto",
        )
        
        msg = resp.choices[0].message
        tool_calls = msg.tool_calls or []
        if tool_calls:
            for tc in tool_calls:
                if tc.function.name == "google_search_func":
                    args = json.loads(tc.function.arguments or "{}")
                    results = google_search_func(**args)
                    return {
                        "action": "search",
                        "query": args.get("query", ""),
                        "results": results
                    }
        
        return {
            "action": "revise",
            "new_text": (msg.content or "").strip()
        }
