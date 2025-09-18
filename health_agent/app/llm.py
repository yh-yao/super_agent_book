from openai import OpenAI
from .config import OPENAI_API_KEY, MODEL_NAME

def get_client() -> OpenAI:
    return OpenAI(api_key=OPENAI_API_KEY)

def complete_with_citations(system_prompt: str, user_prompt: str) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""
