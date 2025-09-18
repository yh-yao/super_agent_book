import os, hashlib, time
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
EMB_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")

def now_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def embed_texts(texts):
    # Returns list of embeddings
    resp = client.embeddings.create(model=EMB_MODEL, input=texts)
    return [d.embedding for d in resp.data]

def chat_json(system_prompt: str, user_prompt: str, max_tokens: int = 700, temperature: float = 0.2):
    resp = client.chat.completions.create(
        model=MODEL,
        temperature=temperature,
        response_format={ "type": "json_object" },
        messages=[
            {"role":"system","content":system_prompt},
            {"role":"user","content":user_prompt}
        ],
        max_tokens=max_tokens
    )
    return resp.choices[0].message.content
