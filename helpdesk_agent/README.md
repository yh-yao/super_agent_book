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
   OPENAI_API_KEY=your-openai-api-key
   PINECONE_API_KEY=your-pinecone-api-key
   PINECONE_INDEX=helpdesk-knowledge
   ```

3. 登录 Pinecone：
   前往 [Pinecone 官网](https://www.pinecone.io/) 注册并获取 API Key，创建一个index，可以命名为helpdesk-knowledge，填入 `.env` 文件。

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
   
更多示例

## 1. 能从 data 找到答案的问答
```bash
curl -X POST http://127.0.0.1:8000/chat \
   -H "Content-Type: application/json" \
   -d '{"session_id":"s2","user_id":"u99","query":"你们的服务时间是什么？"}'
```
返回内容示例：
```json
{"intent":"FAQ","answer":"我们的服务时间是周一至周五，上午9点至下午6点（当地时间）【1】。如果您有其他问题或需要进一步的帮助，请随时联系支持团队。","ticket_id":null,"meta":{}}
```

## 2. 未命中知识库时的问答
```bash
curl -X POST http://127.0.0.1:8000/chat \
   -H "Content-Type: application/json" \
   -d '{"session_id":"s1","user_id":"u42","query":"发票要如何开具？"}'
```
返回内容示例：
```json
{"intent":"FAQ","answer":"很抱歉，检索结果中没有关于发票开具的具体信息。如果您需要详细的发票开具流程，建议您转工单或直接联系相关支持部门。您可以通过发送邮件至 support@helpdesk.com 或拨打 1-800-555-1234 来获取帮助。","ticket_id":null,"meta":{}}
```

## 3. 反馈接口（feedback）
```bash
curl -X POST http://127.0.0.1:8000/feedback \
   -H "Content-Type: application/json" \
   -d '{"session_id":"s2","score":5,"comment":"回复很及时，谢谢！"}'
```
返回结果：
```json
{"ok": true}
```
反馈结果仅为 {"ok": true}，用于记录用户评分和评论。
   
