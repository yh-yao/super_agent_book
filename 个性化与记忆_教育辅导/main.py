from __future__ import annotations
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from edu_agent.syllabus import Syllabus
from edu_agent.questions import QuestionBank
from edu_agent.memory import MemoryDB
from edu_agent.adapt import AdaptivePolicy
from edu_agent.engine import session_once, show_report, show_ai_advice, chat_with_ai

# 数据目录和内存路径配置
DATA_DIR = Path(__file__).resolve().parent / "data"
MEM_PATH = DATA_DIR / "memory.json"

console = Console()

def ask_multiple_choice(stem: str, options):
    """显示多选题并获取用户选择"""
    console.print("\n" + stem)
    for i, opt in enumerate(options):
        console.print(f"  {i}. {opt}")
    idx = IntPrompt.ask("选择选项索引", default=0)
    return idx

def ask_free(stem: str):
    """显示开放题并获取用户答案"""
    console.print("\n" + stem)
    ans = Prompt.ask("你的答案")
    return ans

def main():
    console.rule("[bold blue]英语学习智能助手")
    
    # 加载系统组件
    syllabus = Syllabus.load(DATA_DIR / "syllabus_en.json")
    bank = QuestionBank.load(DATA_DIR / "questions_en.json")
    db = MemoryDB(MEM_PATH)
    policy = AdaptivePolicy(review_ratio=0.6)

    # 获取用户信息
    user_id = Prompt.ask("请输入用户ID", default="s001")
    name = Prompt.ask("学生姓名", default="Alice")
    profile = db.get_student(user_id, name)

    while True:
        console.rule(f"[bold]学习会话 - 当前水平≈{profile.level}")
        
        # 自适应选择题目
        q = policy.select_question(bank, profile)
        if not q:
            console.print("[red]暂无可用题目，请扩充题库。[/red]")
            break

        # 根据题目类型获取用户答案
        if q.options:
            ua = ask_multiple_choice(q.stem, q.options)
        else:
            ua = ask_free(q.stem)

        # 处理答题结果并更新记忆
        session_once(db, profile, policy, q, ua)

        # 获取用户后续操作
        cmd = Prompt.ask("\n[回车] 继续 | r:查看报告 | a:AI建议 | c:与AI聊天 | q:退出", default="")
        if cmd.lower() == "r":
            show_report(profile)
            show_ai_advice(profile)
        elif cmd.lower() == "a":
            show_ai_advice(profile)
        elif cmd.lower() == "c":
            user_input = Prompt.ask("💬 和AI说点什么")
            if user_input.strip():
                ai_response = chat_with_ai(profile, user_input)
                console.print(f"🤖 [cyan]{ai_response}[/cyan]")
        elif cmd.lower() == "q":
            show_report(profile)
            show_ai_advice(profile)
            console.print("[green]再见！[/green]")
            break

if __name__ == "__main__":
    main()