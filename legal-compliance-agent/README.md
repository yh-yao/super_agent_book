# 法律合规助手 (MVP)

一个可运行的**法律合规助手**，用于法规问答（RAG）、基础合规差距分析和轻量级合同审查演示。
使用**FastAPI**、**FAISS**和**OpenAI**（聊天+嵌入）构建。

> ⚠️ 此工具**不**提供法律建议。它是一个辅助系统，必须由合格的法律顾问审查。

## 注意事项
- 首次运行时，应用程序将从`ingest/corpus/`中的示例语料库**构建FAISS索引**
- 您可以添加自己的法规文本作为`.txt`或`.md`文件；重启服务器以重新索引（或删除`vectorstore/*`）
- 将`policies/`中的示例YAML替换为您组织的映射控制措施
- 所有输出都包含免责声明，旨在供**人工审查**

## 功能特性 (MVP)
- 基于示例GDPR/CCPA文本的RAG问答，包含**引用**和**时间戳**
- 基于小型演示政策集的合规差距分析（YAML → 控制措施）
- 合同审查演示：提取几个关键条款并与基线进行比较
- 审计日志，包含提示/响应哈希值和时间戳

## 快速开始

1) **Python环境**
```bash
pip install -r requirements.txt
```

2) **设置环境变量**
从示例创建`.env`文件并填入您的密钥：
```bash
cp .env.example .env
# 编辑 .env
```

3) **运行API**
```bash
# 确保在legal-compliance-agent目录下运行
cd /path/to/legal-compliance-agent
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

服务器启动后，访问 http://127.0.0.1:8000/docs 查看自动生成的API文档。

## API使用示例

### 1. 健康检查
```bash
curl http://127.0.0.1:8000/healthz
```

### 2. 法规问答 (QA)

#### 基础GDPR问题
```bash
curl -X POST http://127.0.0.1:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "GDPR对处理记录有什么规定？",
    "jurisdictions": ["EU"],
    "as_of": "2025-09-01"
  }'
```

#### 数据主体权利问题
```bash
curl -X POST http://127.0.0.1:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "个人有权要求删除其个人数据吗？",
    "jurisdictions": ["EU"],
    "as_of": "2025-09-01"
  }'
```

#### 数据保护官(DPO)相关问题
```bash
curl -X POST http://127.0.0.1:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "什么情况下必须指定数据保护官？",
    "jurisdictions": ["EU"]
  }'
```

#### CCPA相关问题
```bash
curl -X POST http://127.0.0.1:8000/api/qa \
  -H "Content-Type: application/json" \
  -d '{
    "question": "加州消费者隐私法对企业有什么要求？",
    "jurisdictions": ["US", "CA"],
    "as_of": "2025-09-01"
  }'
```

### 3. 合规差距分析

#### 创建测试数据文件
```bash
# 创建示例事实文件
cat > fact_example.json << EOF
{
  "company_name": "示例科技公司",
  "business_type": "SaaS软件服务",
  "data_types": ["用户个人信息", "支付信息", "行为数据"],
  "processing_purposes": ["服务提供", "产品改进", "营销"],
  "data_subjects": ["欧盟居民", "加州居民"],
  "retention_period": "24个月",
  "third_party_sharing": true,
  "cross_border_transfer": true,
  "security_measures": ["加密", "访问控制", "定期审计"]
}
EOF
```

#### 运行合规差距分析
```bash
curl -X POST http://127.0.0.1:8000/api/compliance/gap \
  -H "Content-Type: application/json" \
  -d @fact_example.json
```

#### 指定特定政策的差距分析
```bash
curl -X POST http://127.0.0.1:8000/api/compliance/gap \
  -H "Content-Type: application/json" \
  -d '{
    "fact": {
      "company_name": "全球电商平台",
      "business_type": "电子商务",
      "data_types": ["客户信息", "交易记录", "浏览历史"],
      "processing_purposes": ["订单处理", "客户服务", "个性化推荐"],
      "data_subjects": ["全球用户"],
      "retention_period": "36个月",
      "third_party_sharing": true,
      "cross_border_transfer": true
    },
    "policies": ["gdpr", "ccpa"]
  }'
```

### 4. 合同审查

#### 创建示例合同文件
```bash
cat > sample_contract.txt << EOF
软件许可协议

第一条 许可范围
许可方同意向被许可方提供软件使用权，期限为12个月。

第二条 付款条款
被许可方应在签署本协议后30天内支付许可费用50,000元。

第三条 保密条款
双方应对在履行本协议过程中获得的对方商业秘密承担保密义务。

第四条 责任限制
许可方对因使用软件导致的任何损失不承担赔偿责任。

第五条 争议解决
因本协议产生的争议应通过友好协商解决，协商不成的，提交北京仲裁委员会仲裁。
EOF
```

#### 运行合同审查
```bash
curl -X POST http://127.0.0.1:8000/api/contracts/review \
  -F "file=@sample_contract.txt"
```

#### 审查另一个合同示例
```bash
cat > service_agreement.txt << EOF
云服务协议

第一条 服务内容
服务提供商向客户提供云计算服务，包括但不限于存储、计算、网络服务。

第二条 服务水平
服务可用性承诺99.9%，如未达到将提供服务费用折扣。

第三条 数据安全
服务提供商承诺采用行业标准安全措施保护客户数据。

第四条 终止条款
任一方可提前30天书面通知终止本协议。
EOF

curl -X POST http://127.0.0.1:8000/api/contracts/review \
  -F "file=@service_agreement.txt"
```

## Python客户端示例

```python
import requests
import json

# API基础URL
BASE_URL = "http://127.0.0.1:8000"

def test_qa_api():
    """测试法规问答API"""
    url = f"{BASE_URL}/api/qa"
    
    questions = [
        {
            "question": "GDPR规定的个人数据处理的法律依据有哪些？",
            "jurisdictions": ["EU"],
            "as_of": "2025-09-01"
        },
        {
            "question": "企业如何履行数据可携带权？",
            "jurisdictions": ["EU"]
        },
        {
            "question": "什么是个人信息销售的选择退出权？",
            "jurisdictions": ["US", "CA"]
        }
    ]
    
    for i, question in enumerate(questions):
        print(f"\n=== 问题 {i+1} ===")
        print(f"问题: {question['question']}")
        
        response = requests.post(url, json=question)
        if response.status_code == 200:
            result = response.json()
            print(f"答案: {result['answer']}")
            print(f"置信度: {result['confidence']}")
            print(f"引用数量: {len(result['citations'])}")
        else:
            print(f"请求失败: {response.status_code}")

def test_compliance_gap():
    """测试合规差距分析"""
    url = f"{BASE_URL}/api/compliance/gap"
    
    fact = {
        "company_name": "创新AI公司",
        "business_type": "人工智能服务",
        "data_types": ["用户输入数据", "模型训练数据", "使用统计"],
        "processing_purposes": ["AI模型训练", "服务改进", "研究开发"],
        "data_subjects": ["全球用户"],
        "retention_period": "不确定",
        "third_party_sharing": False,
        "cross_border_transfer": True,
        "security_measures": ["数据加密", "访问日志"]
    }
    
    response = requests.post(url, json={"fact": fact})
    if response.status_code == 200:
        result = response.json()
        print(f"\n=== 合规差距分析 ===")
        print(f"发现 {len(result['gaps'])} 个潜在合规问题")
        for gap in result['gaps'][:3]:  # 显示前3个
            print(f"- 控制措施: {gap['control_id']}")
            print(f"  状态: {gap['status']}")
            print(f"  风险级别: {gap['risk']}")
    else:
        print(f"请求失败: {response.status_code}")

if __name__ == "__main__":
    test_qa_api()
    test_compliance_gap()
```

## 故障排除

### 常见问题

1. **服务器无法启动**
   ```bash
   # 检查依赖是否正确安装
   pip list | grep -E "(fastapi|uvicorn|openai|faiss)"
   
   # 检查环境变量
   cat .env
   ```

2. **404错误**
   ```bash
   # 确保在正确的目录下启动服务器
   pwd  # 应该显示 .../legal-compliance-agent
   ls app/main.py  # 应该存在
   ```

3. **向量存储构建失败**
   ```bash
   # 检查语料库文件
   ls ingest/corpus/
   
   # 删除现有索引重新构建
   rm -rf vectorstore/
   ```

4. **OpenAI API错误**
   ```bash
   # 检查API密钥是否有效
   curl -H "Authorization: Bearer $OPENAI_API_KEY" \
        https://api.openai.com/v1/models
   ```

## 示例文件说明

`examples/` 目录包含以下示例文件：

### 数据文件
- `fact.json` - 基础企业合规事实示例
- `ecommerce_fact.json` - 电商平台详细合规分析示例
- `sample_contract.txt` - 基础软件许可协议示例  
- `cloud_service_contract.txt` - 云服务协议示例

### 测试工具
- `test_client.py` - Python API客户端，包含所有端点的详细测试
- `quick_test.sh` - Bash快速测试脚本，验证基本功能

### 运行示例
```bash
# 运行Python测试客户端
cd legal-compliance-agent
python examples/test_client.py

# 运行快速测试脚本  
./examples/quick_test.sh

# 使用特定示例文件测试
curl -X POST http://127.0.0.1:8000/api/compliance/gap \
  -H "Content-Type: application/json" \
  -d @examples/ecommerce_fact.json
```
