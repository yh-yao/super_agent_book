from __future__ import annotations
from typing import Any, Tuple
from rich.console import Console
from rich.table import Table
from datetime import datetime
from .memory import MemoryDB, QARecord, StudentProfile
from .questions import Question
from .adapt import AdaptivePolicy
from .llm_assistant import get_llm_assistant

console = Console()

def grade(q: Question, user_answer: Any) -> Tuple[bool, str]:
    """
    判分函数：评判用户答案是否正确
    - 优先使用LLM进行智能判分和解释生成
    - 降级到传统字符串匹配
    """
    llm_assistant = get_llm_assistant()
    
    # 如果LLM可用，使用智能判分
    if llm_assistant:
        try:
            is_correct, explanation, confidence = llm_assistant.smart_grade(q, user_answer)
            # 如果置信度过低，可以考虑人工审核或其他处理
            if confidence < 0.3:
                console.print(f"[yellow]⚠️ 判分置信度较低 ({confidence:.2f})，建议复查[/yellow]")
            return is_correct, explanation
        except Exception as e:
            console.print(f"[red]LLM判分失败: {e}[/red]")
            # 降级到传统判分
    
    # 传统判分逻辑
    correct = q.answer
    if isinstance(correct, str):
        ok = str(user_answer).strip().lower() == correct.strip().lower()
    else:
        ok = user_answer == correct
    explain = q.explain or ("做得很好！" if ok else f"正确答案: {correct}")
    return ok, explain

def session_once(db: MemoryDB, profile: StudentProfile, policy: AdaptivePolicy, q: Question, user_answer: Any):
    """
    处理单次答题会话：
    1. 判分
    2. 记录答题历史
    3. 更新学生档案和技能统计
    4. 显示结果和解释
    """
    is_correct, explain = grade(q, user_answer)
    
    # 创建答题记录
    rec = QARecord(
        qid=q.id,
        ts=datetime.utcnow().isoformat(timespec="seconds"),
        is_correct=is_correct,
        cefr=q.cefr,
        tags=q.tags,
        difficulty=q.difficulty,
        user_answer=user_answer,
        correct_answer=q.answer
    )
    
    # 记录到数据库并更新学生档案
    db.log_interaction(profile, rec)

    # 显示答题结果
    if is_correct:
        console.print(f"\n[b]你的答案:[/b] {user_answer}  ->  [green]正确！[/green]")
    else:
        console.print(f"\n[b]你的答案:[/b] {user_answer}  ->  [red]错误[/red]")
    console.print(f"[dim]{explain}[/dim]")
    return is_correct

def show_report(profile: StudentProfile):
    """显示学生的学习报告，包括各技能点的掌握情况"""
    table = Table(title=f"{profile.name} ({profile.user_id}) 的学习报告  |  当前水平≈{profile.level}")
    table.add_column("技能标签")
    table.add_column("掌握度", justify="right")
    table.add_column("正确/错误", justify="right")
    table.add_column("下次复习时间 (UTC)")
    
    # 按掌握度从高到低排序显示
    for tag, stat in sorted(profile.skills.items(), key=lambda kv: kv[1].mastery, reverse=True):
        table.add_row(
            tag,
            f"{stat.mastery:.2f}",
            f"{stat.correct}/{stat.wrong}",
            stat.next_review or "-"
        )
    console.print(table)

def show_ai_advice(profile: StudentProfile):
    """显示AI生成的个性化学习建议"""
    llm_assistant = get_llm_assistant()
    
    if llm_assistant:
        console.print("\n[bold cyan]🤖 AI学习建议[/bold cyan]")
        try:
            advice = llm_assistant.generate_learning_advice(profile)
            console.print(f"[dim]{advice}[/dim]")
        except Exception as e:
            console.print(f"[red]AI建议生成失败: {e}[/red]")
    else:
        console.print("\n[yellow]💡 学习建议[/yellow]")
        console.print("[dim]继续练习，保持学习的节奏！[/dim]")

def chat_with_ai(profile: StudentProfile, user_input: str) -> str:
    """与AI助手聊天"""
    llm_assistant = get_llm_assistant()
    
    if llm_assistant:
        try:
            return llm_assistant.chat_with_student(user_input, profile)
        except Exception as e:
            return f"抱歉，AI助手暂时不可用: {e}"
    else:
        return "AI助手未启用，请继续你的学习！"
