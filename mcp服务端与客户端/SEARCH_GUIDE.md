# 搜索功能使用指南

## 概述

MCP 演示项目的搜索工具支持两种模式：

1. **演示模式**（默认）- 无需配置，返回预设的演示数据
2. **真实搜索模式** - 需要配置 SerpAPI Key，支持百度、Google、Bing 等多个搜索引擎

## 模式 1: 演示模式（推荐用于学习）

### 使用方法

直接运行，无需任何配置：

```bash
python client/demo_client.py
# 或
python client/openai_client.py  # 需要 OPENAI_API_KEY
```

### 特点

- ✅ 无需注册和申请 API Key
- ✅ 立即可用，适合学习和测试
- ✅ 包含精心准备的 MCP 相关演示数据
- ⚠️ 仅返回预设的演示结果，不是真实搜索

### 演示查询

系统预设了以下查询的演示数据：
- "Python MCP" - 返回 MCP 协议和 Python SDK 的相关信息

其他查询会返回提示信息，说明如何启用真实搜索。

## 模式 2: 真实搜索模式（生产环境）

### 1. 注册 SerpAPI

访问 https://serpapi.com 注册账号：
- 提供免费额度（每月 100 次搜索）
- 支持百度、Google、Bing 等多个搜索引擎
- 无需信用卡即可开始使用免费额度

### 2. 获取 API Key

登录后在 Dashboard 页面找到你的 API Key。

### 3. 设置环境变量

```bash
export SERPAPI_API_KEY='your-serpapi-key-here'
```

或者在 `.env` 文件中添加：
```
SERPAPI_API_KEY=your-serpapi-key-here
```

### 4. 使用真实搜索

运行客户端时，搜索工具会自动使用真实 API：

```bash
python client/demo_client.py
```

### 支持的搜索引擎

修改工具调用时的 `engine` 参数：

```python
# 百度搜索（默认）
session.call_tool("search_http", {"query": "人工智能", "engine": "baidu"})

# Google 搜索
session.call_tool("search_http", {"query": "artificial intelligence", "engine": "google"})

# Bing 搜索
session.call_tool("search_http", {"query": "AI news", "engine": "bing"})
```

### 返回结果格式

```python
[
    {
        "title": "结果标题",
        "snippet": "结果摘要或描述",
        "url": "https://example.com"
    },
    # ... 最多 5 个结果
]
```

## 错误处理

搜索工具具有完善的错误处理机制：

1. **API Key 无效或配额用尽** - 自动降级到演示模式
2. **网络错误** - 返回错误提示并降级到演示模式
3. **搜索无结果** - 返回空列表 `[]`

## 成本说明

### SerpAPI 定价（2025年）

- **免费额度**: 100 次搜索/月
- **付费套餐**: 从 $50/月起（5000 次搜索）

### 百度搜索 API（官方）

如果需要大量使用百度搜索，可以考虑：
- 百度智能云 - 网页搜索 API
- 需要企业认证
- 按调用次数计费

## 最佳实践

### 开发和学习阶段
- 使用演示模式，无需配置
- 专注于学习 MCP 协议和工具集成

### 测试阶段
- 使用 SerpAPI 免费额度
- 测试真实搜索场景

### 生产环境
- 评估搜索调用频率
- 选择合适的 API 套餐
- 添加缓存机制减少 API 调用
- 监控 API 配额使用情况

## 扩展建议

如需更高级的功能，可以考虑：

1. **添加搜索结果缓存**
   ```python
   # 使用 Redis 或内存缓存减少 API 调用
   ```

2. **支持更多搜索引擎**
   ```python
   # SerpAPI 支持 30+ 搜索引擎
   # 包括 Yahoo, DuckDuckGo, Yandex 等
   ```

3. **高级搜索功能**
   ```python
   # 图片搜索、新闻搜索、学术搜索等
   ```

4. **搜索结果过滤和排序**
   ```python
   # 按时间、相关性、语言等过滤
   ```

## 故障排查

### 问题：设置了 API Key 但仍使用演示模式

检查：
- 环境变量是否正确设置：`echo $SERPAPI_API_KEY`
- API Key 是否有效（登录 SerpAPI 查看）
- 是否重启了服务器进程

### 问题：搜索返回错误

可能原因：
- API Key 配额已用完
- 网络连接问题
- 搜索引擎参数不正确

查看服务器日志中的详细错误信息（输出到 stderr）。

## 相关资源

- SerpAPI 官网: https://serpapi.com
- SerpAPI 文档: https://serpapi.com/docs
- 百度搜索 API: https://cloud.baidu.com/product/search
- MCP 官方文档: https://modelcontextprotocol.io
