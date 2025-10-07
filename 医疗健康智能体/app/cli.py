import argparse, requests, json

def format_output(response_data):
    """Format the response for better readability"""
    print("=" * 80)
    print("🏥 健康智能助手 - 回复详情")
    print("=" * 80)
    
    # 主要回答
    if "answer" in response_data:
        print("\n📋 回答内容:")
        print("-" * 40)
        print(response_data["answer"])
    
    # 重要警告信息
    if "disclaimer" in response_data:
        print("\n⚠️  重要提醒:")
        print("-" * 40)
        print(response_data["disclaimer"])
    
    # 风险分级
    if "policy" in response_data:
        policy = response_data["policy"]
        triage_level = policy.get("triage_level", "未知")
        blocked = policy.get("blocked", False)
        
        print(f"\n🚨 风险分级: {triage_level.upper()}")
        print("-" * 40)
        
        if triage_level == "red":
            print("🔴 高风险 - 建议立即就医!")
        elif triage_level == "yellow":
            print("🟡 中等风险 - 建议尽快就医")
        elif triage_level == "green":
            print("🟢 低风险 - 可观察或预约门诊")
        
        if blocked:
            print("⛔ 该查询已被系统阻止")
        
        if "reasons" in policy and policy["reasons"]:
            print(f"原因: {', '.join(policy['reasons'])}")
    
    # 参考文献
    if "citations" in response_data and response_data["citations"]:
        print(f"\n📚 参考资料 ({len(response_data['citations'])} 条):")
        print("-" * 40)
        for i, citation in enumerate(response_data["citations"], 1):
            title = citation.get("title", "未知来源")
            score = citation.get("score", 0)
            print(f"[{i}] {title} (相关度: {score:.2f})")
            
            chunk = citation.get("chunk", "")
            if chunk:
                # 只显示前100个字符
                preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
                print(f"    内容预览: {preview}")
    
    # 元数据
    if "meta" in response_data:
        meta = response_data["meta"]
        phi_scrubbed = meta.get("phi_scrubbed", False)
        print(f"\n🔒 隐私保护: {'已启用' if phi_scrubbed else '未启用'}")
    
    print("\n" + "=" * 80)

def main():
    p = argparse.ArgumentParser(description="健康智能助手命令行工具")
    p.add_argument("--host", default="http://127.0.0.1:8000", help="服务器地址")
    p.add_argument("--question", required=True, help="要咨询的健康问题")
    p.add_argument("--user_id", default="demo_user", help="用户ID")
    p.add_argument("--raw", action="store_true", help="显示原始JSON响应")
    args = p.parse_args()
    
    payload = {"user_id": args.user_id, "question": args.question}
    
    try:
        print(f"🔍 正在查询: {args.question}")
        print(f"🌐 服务器: {args.host}")
        print("⏳ 请稍等...")
        
        r = requests.post(args.host + "/ask", json=payload, timeout=60)
        r.raise_for_status()
        
        response_data = r.json()
        
        if args.raw:
            print(json.dumps(response_data, ensure_ascii=False, indent=2))
        else:
            format_output(response_data)
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {e}")
    except json.JSONDecodeError as e:
        print(f"❌ 响应解析失败: {e}")
    except Exception as e:
        print(f"❌ 发生错误: {e}")

if __name__ == "__main__":
    main()
