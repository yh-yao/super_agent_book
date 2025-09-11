# Doc Assistant

基于 LangChain + FAISS + FastAPI 的企业文档助手。
支持 PDF 文档解析、向量化索引、多轮问答与引用追踪。

## 使用方法

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 构建向量索引：
   ```bash
   python ingest/index_faiss.py
   ```

3. 启动服务：
   ```bash
   uvicorn app.main:app --reload --port 8001
   ```

4. 调用示例：
   ```bash
   curl -X POST http://127.0.0.1:8001/chat      -H "Content-Type: application/json"      -d '{"session_id":"s1","query":"公司报销制度是怎样的？"}'
   ```
