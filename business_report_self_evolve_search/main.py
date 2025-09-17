import argparse
import json
from agent import SelfEvolvingAgent





def write_json(path: str, data):
    """将数据写入JSON文件。"""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    """运行自进化商业报告生成代理的主函数。"""
    ap = argparse.ArgumentParser(
        description="自进化商业报告生成代理（搜索 + LLM）"
    )
    ap.add_argument(
        "--prompt", type=str, required=True, help="输入提示词"
    )
    ap.add_argument("--steps", type=int, default=5, help="迭代步数")
    ap.add_argument("--out", type=str, default="out.json", help="输出文件")
    ap.add_argument("--target-score", type=float, default=0.86, help="目标分数")
    ap.add_argument("--target-words", type=int, default=800, help="目标字数")
    args = ap.parse_args()

    agent = SelfEvolvingAgent()
    source = args.prompt
    summary, meta = agent.run(
        source_text=source, 
        steps=args.steps, 
        target_score=args.target_score,
        target_words=args.target_words
    )
    result = {"summary": summary, **meta}
    write_json(args.out, result)

    print("=== 生成的商业报告 ===")
    print(summary)
    print("\n=== 最佳评分 ===")
    print(json.dumps(meta["best_score"], ensure_ascii=False, indent=2))
    
    # 显示搜索结果摘要
    if "search_summary" in meta and meta["search_summary"]:
        print(f"\n=== 搜索摘要 ===")
        print(f"共进行了 {len(meta['search_summary'])} 次搜索:")
        for search in meta["search_summary"]:
            print(f"  步骤 {search['step']}: {search['query']} (找到 {len(search['results'])} 个结果)")
    
    print(f"\n结果已保存到 {args.out}")


if __name__ == "__main__":
    main()
