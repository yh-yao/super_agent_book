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
    try:
        if not texts:
            return []
        
        # 检查API密钥
        if not client.api_key:
            raise ValueError("OpenAI API key not configured")
        
        print(f"      📡 调用OpenAI API处理 {len(texts)} 个文本...")
        start_time = time.time()
        
        resp = client.embeddings.create(
            model=EMB_MODEL, 
            input=texts,
            timeout=30  # 30秒超时
        )
        
        elapsed = time.time() - start_time
        print(f"      ⏱️ API调用完成，耗时 {elapsed:.2f}秒")
        
        return [d.embedding for d in resp.data]
        
    except Exception as e:
        print(f"❌ 嵌入生成失败: {e}")
        print(f"   模型: {EMB_MODEL}")
        print(f"   文本数量: {len(texts)}")
        if texts:
            print(f"   文本长度: {[len(t) for t in texts]}")
        raise

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
