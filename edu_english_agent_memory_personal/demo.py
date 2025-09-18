#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示脚本：展示不同级别学生的学习过程
"""

import json
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

def load_memory_example(filename):
    """加载示例记忆数据"""
    data_dir = Path(__file__).parent / "data"
    file_path = data_dir / filename
    
    if not file_path.exists():
        console.print(f"[red]示例文件不存在: {filename}[/red]")
        return None
        
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def show_student_profile(student_data, title):
    """显示学生档案信息"""
    console.print(Panel(title, style="bold blue"))
    
    # 基本信息
    console.print(f"[bold]学生姓名:[/bold] {student_data['name']}")
    console.print(f"[bold]用户ID:[/bold] {student_data['user_id']}")
    console.print(f"[bold]当前等级:[/bold] {student_data['level']}")
    console.print()
    
    # 技能统计表格
    table = Table(title=f"{student_data['name']} 的技能掌握情况")
    table.add_column("技能标签", style="cyan")
    table.add_column("掌握度", justify="right", style="green")
    table.add_column("正确/错误", justify="right")
    table.add_column("下次复习时间")
    
    for tag, stat in sorted(student_data['skills'].items(), 
                           key=lambda x: x[1]['mastery'], reverse=True):
        mastery_color = "green" if stat['mastery'] >= 0.7 else "yellow" if stat['mastery'] >= 0.4 else "red"
        table.add_row(
            tag,
            f"[{mastery_color}]{stat['mastery']:.2f}[/{mastery_color}]",
            f"{stat['correct']}/{stat['wrong']}",
            stat['next_review'].split('T')[0] if stat['next_review'] else "-"
        )
    
    console.print(table)
    console.print()

def show_learning_history(student_data, title):
    """显示最近的学习历史"""
    console.print(Panel(f"{title} - 最近答题历史", style="bold yellow"))
    
    recent_history = student_data['history'][-5:]  # 显示最近5条记录
    
    for i, record in enumerate(recent_history, 1):
        status = "✓" if record['is_correct'] else "✗"
        status_color = "green" if record['is_correct'] else "red"
        console.print(f"{i}. [{status_color}]{status}[/{status_color}] "
                     f"题目{record['qid']} ({record['cefr']}) "
                     f"- {', '.join(record['tags'])} "
                     f"- 难度{record['difficulty']:.1f}")
    console.print()

def show_adaptive_recommendation(student_data):
    """显示自适应推荐"""
    console.print(Panel("系统推荐", style="bold magenta"))
    
    level = student_data['level']
    skills = student_data['skills']
    
    # 找出掌握度最低的技能
    weak_skills = sorted(skills.items(), key=lambda x: x[1]['mastery'])[:3]
    
    console.print(f"[bold]基于当前等级 {level} 的推荐:[/bold]")
    console.print(f"• 60% 时间复习薄弱技能: {', '.join([skill[0] for skill in weak_skills])}")
    console.print(f"• 40% 时间探索 {level} 级别新内容")
    console.print()
    
    for skill, stat in weak_skills:
        if stat['mastery'] < 0.5:
            console.print(f"[yellow]⚠ 需要重点关注:[/yellow] {skill} (掌握度: {stat['mastery']:.2f})")

def main():
    """主演示函数"""
    console.rule("[bold blue]英语学习智能助手 - 演示", style="bold blue")
    console.print()
    
    # 演示低级别学生
    beginner_data = load_memory_example("memory_example_beginner.json")
    if beginner_data:
        student = beginner_data['students']['xiaoming']
        show_student_profile(student, "低级别学生案例 (A1水平)")
        show_learning_history(student, "小明")
        show_adaptive_recommendation(student)
    
    console.rule("", style="dim")
    console.print()
    
    # 演示高级别学生
    advanced_data = load_memory_example("memory_example_advanced.json")
    if advanced_data:
        student = advanced_data['students']['lihua']
        show_student_profile(student, "高级别学生案例 (B2水平)")
        show_learning_history(student, "李华")
        show_adaptive_recommendation(student)
    
    console.rule("")
    console.print("[bold green]演示完成！[/bold green]")
    console.print("运行 [bold cyan]python main.py[/bold cyan] 开始实际学习会话")

if __name__ == "__main__":
    main()