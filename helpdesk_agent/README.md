# Helpdesk AI

基于 LangChain + Pinecone + FastAPI 的企业客服智能体。
支持 FAQ 问答、工单生成、投诉处理与多轮记忆。

## 使用方法

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 创建 `.env` 文件：
   在 `helpdesk_agent` 目录下新建 `.env` 文件，内容如下：
   ```env
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_INDEX=helpdesk-knowledge
   ```

3. 登录 Pinecone：
   前往 [Pinecone 官网](https://www.pinecone.io/) 注册并获取 API Key，填入 `.env` 文件。

4. 向量模型与维度：
   本项目使用 `text-embedding-3-small` 模型，维度为 `512`。请确保 Pinecone Index 创建时维度为 512。

5. 构建向量索引：
   ```bash
   python ingest/index_pinecone.py
   ```

6. 启动服务：
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

7. 调用示例：
   ```bash
   curl -X POST http://127.0.0.1:8000/chat      -H "Content-Type: application/json"      -d '{"session_id":"s1","user_id":"u42","query":"发票要如何开具？"}'
   ```
