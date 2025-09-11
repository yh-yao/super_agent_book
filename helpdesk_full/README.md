# Helpdesk AI

基于 LangChain + Pinecone + FastAPI 的企业客服智能体。
支持 FAQ 问答、工单生成、投诉处理与多轮记忆。

## 使用方法

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 构建向量索引：
   ```bash
   python ingest/index_pinecone.py
   ```

3. 启动服务：
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

4. 调用示例：
   ```bash
   curl -X POST http://127.0.0.1:8000/chat      -H "Content-Type: application/json"      -d '{"session_id":"s1","user_id":"u42","query":"发票要如何开具？"}'
   ```
