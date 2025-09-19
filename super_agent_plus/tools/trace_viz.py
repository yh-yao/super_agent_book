
import json
from typing import List, Dict

def trace_to_markdown(path: str) -> str:
    data = json.load(open(path, encoding="utf-8"))
    md = ["| Node | Input (user msg) | Outcome | Citations |",
          "|------|-----------------|---------|-----------|"]
    for e in data:
        msg = e["messages_in"][0]["content"] if e["messages_in"] else ""
        outcome = (e["outcome_after"] or "").replace("\n"," ")[:60]
        cites = ", ".join(e["citations"])
        md.append(f"| {e['node']} | {msg} | {outcome} | {cites} |")
    return "\n".join(md)

def trace_to_mermaid(path: str) -> str:
    data = json.load(open(path, encoding="utf-8"))
    mer = ["```mermaid", "sequenceDiagram"]
    mer.append("  participant U as User")
    prev = "U"
    for i,e in enumerate(data):
        node = e["node"]
        content = e["messages_in"][0]["content"] if e["messages_in"] else ""
        outcome = (e["outcome_after"] or "").replace("\n"," ")[:40]
        mer.append(f"  {prev}->>{node}: {content}")
        mer.append(f"  {node}-->>U: {outcome}")
        prev = node
    mer.append("```")
    return "\n".join(mer)

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("trace_file", help="path to runs/trace_xxx.json")
    ap.add_argument("--fmt", choices=["md","mermaid"], default="md")
    args = ap.parse_args()

    if args.fmt == "md":
        print(trace_to_markdown(args.trace_file))
    else:
        print(trace_to_mermaid(args.trace_file))
