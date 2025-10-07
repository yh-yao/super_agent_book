
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class OpenAILLM:
    def __init__(self, model):
        self.model = model

    def chat(self, prompt: str) -> str:
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role":"system","content":"You are a helpful AI."},
                      {"role":"user","content":prompt}],
            temperature=0.3
        )
        return resp.choices[0].message.content

def get_llm(model_name="gpt-4o-mini"):
    return OpenAILLM(model_name)
