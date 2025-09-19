#!/bin/bash

# 法律合规助手快速测试脚本
# 使用方法: chmod +x quick_test.sh && ./quick_test.sh

echo "🚀 法律合规助手 API 快速测试"
echo "=================================="

# 检查服务器是否运行
echo "检查服务器状态..."
if curl -s http://127.0.0.1:8000/healthz > /dev/null; then
    echo "✅ 服务器运行正常"
else
    echo "❌ 服务器未运行，请先启动服务器:"
    echo "   cd /path/to/legal-compliance-agent"
    echo "   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

echo ""
echo "1. 测试GDPR问答..."
curl -X POST http://127.0.0.1:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "GDPR对处理记录有什么规定？",
    "jurisdictions": ["EU"],
    "as_of": "2025-09-01"
  }' \
  -w "\n状态码: %{http_code}\n" \
  -s | jq -r '.answer // "解析失败"' | head -c 200
echo "..."

echo ""
echo "2. 测试数据主体权利问答..."
curl -X POST http://127.0.0.1:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "个人有权要求删除其个人数据吗？",
    "jurisdictions": ["EU"]
  }' \
  -w "\n状态码: %{http_code}\n" \
  -s | jq -r '.answer // "解析失败"' | head -c 200
echo "..."

echo ""
echo "3. 测试CCPA问答..."
curl -X POST http://127.0.0.1:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "加州消费者隐私法对企业有什么要求？",
    "jurisdictions": ["US", "CA"]
  }' \
  -w "\n状态码: %{http_code}\n" \
  -s | jq -r '.answer // "解析失败"' | head -c 200
echo "..."

echo ""
echo "4. 测试合规差距分析..."
if [ -f "examples/fact.json" ]; then
    curl -X POST http://127.0.0.1:8000/api/compliance/gap \
      -H "Content-Type: application/json" \
      -d @examples/fact.json \
      -w "\n状态码: %{http_code}\n" \
      -s | jq -r '.gaps | length // 0' | xargs -I {} echo "发现 {} 个合规问题"
else
    echo "❌ 示例文件 examples/fact.json 不存在"
fi

echo ""
echo "5. 测试合同审查..."
if [ -f "examples/sample_contract.txt" ]; then
    curl -X POST http://127.0.0.1:8000/api/contracts/review \
      -F "file=@examples/sample_contract.txt" \
      -w "\n状态码: %{http_code}\n" \
      -s | jq -r '.risks | length // 0' | xargs -I {} echo "发现 {} 个风险项"
else
    echo "❌ 示例文件 examples/sample_contract.txt 不存在"
fi

echo ""
echo "=================================="
echo "✅ 快速测试完成！"
echo "💡 查看完整API文档: http://127.0.0.1:8000/docs"
echo "💡 运行详细测试: python examples/test_client.py"