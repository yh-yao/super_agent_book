import os, json, glob, re, time
import numpy as np
import faiss
from typing import List, Tuple, Dict
from .llm import embed_texts

VSTORE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "vectorstore")
CORPUS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ingest", "corpus")

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
TOP_K = int(os.getenv("TOP_K","6"))

def _split_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    chunks = []
    start = 0
    
    # 确保overlap小于chunk_size，避免无限循环
    if overlap >= chunk_size:
        overlap = chunk_size // 2
    
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunk = text[start:end]
        
        # 只添加非空块
        if chunk.strip():
            chunks.append(chunk)
        
        # 计算下一个起始位置
        next_start = end - overlap
        
        # 防止无限循环：确保每次都向前推进
        if next_start <= start:
            next_start = start + 1
            
        start = next_start
        
        # 如果已经到达文本末尾，退出
        if end >= len(text):
            break
            
        # 防止意外的无限循环（安全措施）
        if len(chunks) > 1000:  # 假设不会有超过1000个块
            print(f"⚠️ 警告：文本分割产生了过多块数 ({len(chunks)})，可能存在问题")
            break
    
    return chunks

def _load_corpus() -> List[Dict]:
    files = glob.glob(os.path.join(CORPUS_DIR, "*.*"))
    out = []
    print(f"📁 处理语料库文件: {len(files)} 个文件")
    
    for fp in files:
        try:
            with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                txt = f.read()
            title = os.path.basename(fp)
            print(f"   📄 处理文件: {title}")
            
            # 尝试提取日期信息（支持中英文）
            date = None
            # 英文格式
            m_date = re.search(r"Effective date:\s*([0-9\-]+)", txt)
            if m_date:
                date = m_date.group(1)
            else:
                # 中文格式
                m_date = re.search(r"生效日期[：:]\s*([0-9\-]+)", txt)
                if m_date:
                    date = m_date.group(1)
            
            # 尝试提取来源信息（支持中英文）
            src = None
            # 英文格式
            m_src = re.search(r"Source:\s*(.*)$", txt, re.MULTILINE)
            if m_src:
                src = m_src.group(1).strip()
            else:
                # 中文格式
                m_src = re.search(r"来源[：:]\s*(.*)$", txt, re.MULTILINE)
                if m_src:
                    src = m_src.group(1).strip()
            
            chunks = _split_text(txt)
            print(f"      分割为 {len(chunks)} 个块")
            
            for i, ch in enumerate(chunks):
                if ch.strip():  # 只添加非空的文本块
                    out.append({
                        "title": title,
                        "date": date,
                        "url": src,
                        "chunk_id": f"{title}#chunk{i}",
                        "text": ch.strip()
                    })
        except Exception as e:
            print(f"   ❌ 处理文件 {fp} 时出错: {e}")
            continue
    
    print(f"📊 总共生成 {len(out)} 个文档块")
    return out

def _paths():
    return (
        os.path.join(VSTORE_DIR, "index.faiss"),
        os.path.join(VSTORE_DIR, "docs.json")
    )

def build_or_load():
    faiss_path, docs_path = _paths()
    if os.path.exists(faiss_path) and os.path.exists(docs_path):
        index = faiss.read_index(faiss_path)
        with open(docs_path, "r", encoding="utf-8") as f:
            docs = json.load(f)
        return index, docs

    docs = _load_corpus()
    if not docs:
        raise ValueError("语料库为空，无法构建索引")
    
    texts = [d["text"] for d in docs]
    
    # 批量处理嵌入以节省内存和提高效率
    print(f"🔧 开始生成 {len(texts)} 个文本块的嵌入向量...")
    batch_size = 5  # 增加批处理大小提高效率
    all_embs = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_num = i//batch_size + 1
        total_batches = (len(texts)-1)//batch_size + 1
        
        print(f"   🔄 批次 {batch_num}/{total_batches}: 处理 {len(batch_texts)} 个文本块...")
        
        try:
            start_time = time.time()
            batch_embs = embed_texts(batch_texts)
            elapsed = time.time() - start_time
            print(f"      ✅ 完成，耗时 {elapsed:.2f}秒")
            
            all_embs.extend(batch_embs)
            
            # 适当休息避免API限制
            if batch_num < total_batches:
                time.sleep(0.2)
                
        except Exception as e:
            print(f"      ❌ 批次 {batch_num} 处理失败: {e}")
            # 尝试单个处理失败的批次
            print(f"      🔄 尝试单个处理...")
            for j, single_text in enumerate(batch_texts):
                try:
                    single_emb = embed_texts([single_text])
                    all_embs.extend(single_emb)
                    print(f"         ✅ 单个文本 {j+1} 处理成功")
                except Exception as e2:
                    print(f"         ❌ 单个文本 {j+1} 也失败: {e2}")
                    # 使用零向量作为占位符
                    if all_embs:
                        dummy_emb = [0.0] * len(all_embs[0])
                        all_embs.append(dummy_emb)
                        print(f"         ⚠️ 使用零向量占位")
    
    if not all_embs:
        raise ValueError("无法生成任何嵌入向量")
    
    print(f"✅ 嵌入向量生成完成，共 {len(all_embs)} 个")
    
    # 构建FAISS索引
    print("🔧 构建FAISS索引...")
    dim = len(all_embs[0])
    index = faiss.IndexFlatIP(dim)
    
    # Normalize for cosine similarity via inner product
    vecs = np.array(all_embs).astype("float32")
    # L2 normalize
    norms = np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-10
    vecs = vecs / norms
    index.add(vecs)

    # 确保vectorstore目录存在
    os.makedirs(os.path.dirname(faiss_path), exist_ok=True)
    
    # 保存索引和文档
    print("💾 保存索引文件...")
    faiss_path, docs_path = _paths()
    faiss.write_index(index, faiss_path)
    with open(docs_path, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)
    
    print("🎉 索引构建完成！")
    return index, docs

def search(query: str, k: int = TOP_K) -> List[Dict]:
    index, docs = build_or_load()
    q_emb = embed_texts([query])[0]
    q = np.array([q_emb]).astype("float32")
    q = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-10)
    D, I = index.search(q, k)
    hits = []
    for idx, score in zip(I[0], D[0]):
        if idx == -1: continue
        d = dict(docs[idx])
        d["score"] = float(score)
        hits.append(d)
    return hits
