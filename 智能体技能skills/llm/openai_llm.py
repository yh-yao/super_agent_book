import json
from openai import OpenAI

class LLM:
    """调用 OpenAI LLM，将自然语言转为结构化中间表示（IR）"""

    def __init__(self, model: str = "gpt-4o-mini"):
        self.client = OpenAI()
        self.model = model

    def generate_ppt_ir(self, topic: str) -> dict:
        prompt = f"""
你是一个 PPT 结构生成器。
请根据用户输入生成 JSON，不要输出任何解释说明。

JSON 格式必须严格如下：
{{
  "title": "...",
  "slides": [
    {{
      "title": "...",
      "content": ["...", "..."]
    }}
  ]
}}

用户主题：{topic}
"""

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "你是一个结构化输出助手"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        text = resp.choices[0].message.content.strip()
        return json.loads(text)
