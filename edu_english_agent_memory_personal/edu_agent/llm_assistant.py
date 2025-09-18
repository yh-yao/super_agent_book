"""
LLM助手模块：提供智能判分、解释生成和学习建议功能
"""
from __future__ import annotations
import os
from typing import Any, Tuple, Optional, List
from openai import OpenAI
from dotenv import load_dotenv
from .memory import StudentProfile, SkillStat
from .questions import Question

# 加载环境变量
load_dotenv()

class LLMAssistant:
    """LLM助手类，提供各种AI增强功能"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.grading_model = os.getenv("LLM_GRADING_MODEL", self.default_model)
        self.explanation_model = os.getenv("LLM_EXPLANATION_MODEL", self.default_model)
        self.conversation_model = os.getenv("LLM_CONVERSATION_MODEL", self.default_model)
    
    def smart_grade(self, question: Question, user_answer: Any) -> Tuple[bool, str, float]:
        """
        智能判分：使用LLM对学生答案进行语义评估
        
        Returns:
            (is_correct, explanation, confidence): 是否正确、解释、置信度
        """
        # 对于选择题，仍使用传统判分
        if question.options:
            is_correct = user_answer == question.answer
            explanation = self._generate_explanation(question, user_answer, is_correct)
            return is_correct, explanation, 1.0
        
        # 对于开放题，使用LLM进行语义判分
        return self._llm_grade_open_question(question, user_answer)
    
    def _llm_grade_open_question(self, question: Question, user_answer: Any) -> Tuple[bool, str, float]:
        """使用LLM对开放题进行判分"""
        prompt = f"""
作为英语学习助手，请评估学生对以下题目的回答：

题目: {question.stem}
正确答案: {question.answer}
学生答案: {user_answer}
题目等级: {question.cefr}
技能标签: {', '.join(question.tags)}

请从以下几个方面评估：
1. 语义准确性：学生答案是否表达了正确的意思
2. 语法正确性：是否有语法错误
3. 词汇适当性：用词是否合适

请返回JSON格式：
{{
    "is_correct": true/false,
    "confidence": 0.0-1.0,
    "explanation": "详细解释，包括错误分析和改进建议",
    "grammar_issues": ["语法问题列表"],
    "vocabulary_suggestions": ["词汇建议列表"]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.grading_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            import json
            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")
            result = json.loads(content)
            
            return (
                result.get("is_correct", False),
                result.get("explanation", ""),
                result.get("confidence", 0.5)
            )
            
        except Exception as e:
            print(f"LLM判分出错: {e}")
            # 降级到简单字符串匹配
            is_correct = str(user_answer).strip().lower() == str(question.answer).strip().lower()
            return is_correct, f"简单匹配结果。正确答案: {question.answer}", 0.8 if is_correct else 0.3
    
    def _generate_explanation(self, question: Question, user_answer: Any, is_correct: bool) -> str:
        """为选择题生成个性化解释"""
        if question.explain:
            base_explanation = question.explain
        else:
            base_explanation = f"正确答案是: {question.answer}"
        
        # 如果答对了，给予鼓励
        if is_correct:
            return f"✅ 答对了！{base_explanation}"
        
        # 如果答错了，使用LLM生成更详细的解释
        prompt = f"""
学生做错了这道英语题，请生成一个有帮助的解释：

题目: {question.stem}
选项: {question.options}
正确答案: {question.answer}
学生选择: {user_answer}
基础解释: {base_explanation}
难度等级: {question.cefr}

请生成一个简洁但有帮助的解释，包括：
1. 为什么学生的选择是错误的
2. 正确答案的原理
3. 记忆技巧或规律
4. 鼓励性的话语

控制在2-3句话内。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.explanation_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "❌ 解释生成失败"
            
        except Exception as e:
            print(f"解释生成出错: {e}")
            return f"❌ {base_explanation}"
    
    def generate_learning_advice(self, profile: StudentProfile) -> str:
        """根据学生档案生成个性化学习建议"""
        # 分析薄弱技能
        weak_skills = []
        strong_skills = []
        
        for skill, stat in profile.skills.items():
            if stat.mastery < 0.4:
                weak_skills.append((skill, stat.mastery))
            elif stat.mastery > 0.8:
                strong_skills.append((skill, stat.mastery))
        
        weak_skills.sort(key=lambda x: x[1])  # 按掌握度排序
        strong_skills.sort(key=lambda x: x[1], reverse=True)
        
        prompt = f"""
作为英语学习顾问，请为这位学生生成个性化学习建议：

学生信息：
- 姓名: {profile.name}
- 当前等级: {profile.level}
- 总答题数: {len(profile.history)}

薄弱技能 (掌握度 < 0.4):
{chr(10).join([f"- {skill}: {mastery:.2f}" for skill, mastery in weak_skills[:5]])}

强项技能 (掌握度 > 0.8):
{chr(10).join([f"- {skill}: {mastery:.2f}" for skill, mastery in strong_skills[:3]])}

请生成：
1. 针对薄弱技能的具体学习建议
2. 如何利用强项技能来提升整体水平
3. 适合当前等级的学习策略
4. 鼓励性的话语

保持简洁有用，控制在150字内。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.conversation_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "学习建议生成失败"
            
        except Exception as e:
            print(f"学习建议生成出错: {e}")
            return self._generate_simple_advice(weak_skills, strong_skills, profile.level)
    
    def _generate_simple_advice(self, weak_skills: List, strong_skills: List, level: str) -> str:
        """生成简单的学习建议（降级方案）"""
        advice = f"基于你的 {level} 等级表现："
        
        if weak_skills:
            top_weak = weak_skills[0][0]
            advice += f"\n• 重点关注: {top_weak}"
        
        if strong_skills:
            top_strong = strong_skills[0][0]
            advice += f"\n• 继续保持: {top_strong}"
        
        advice += f"\n• 建议多练习当前等级的题目，巩固基础后再挑战更高难度。"
        
        return advice
    
    def chat_with_student(self, user_input: str, profile: StudentProfile) -> str:
        """与学生进行对话交流"""
        prompt = f"""
你是一个友好的英语学习助手。学生向你提问或交流。

学生信息：
- 姓名: {profile.name}  
- 等级: {profile.level}
- 答题历史: {len(profile.history)}题

学生说: {user_input}

请用中文回复，保持友好、有帮助的语调。如果是英语学习相关问题，提供准确的解答。
控制在100字内。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.conversation_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            return content.strip() if content else "抱歉，我现在无法回答这个问题。"
            
        except Exception as e:
            print(f"对话生成出错: {e}")
            return "抱歉，我现在无法回答这个问题。请继续你的学习！"

# 全局LLM助手实例
_llm_assistant = None

def get_llm_assistant() -> Optional[LLMAssistant]:
    """获取LLM助手实例"""
    global _llm_assistant
    
    if _llm_assistant is None:
        try:
            _llm_assistant = LLMAssistant()
            # 测试连接
            test_response = _llm_assistant.client.chat.completions.create(
                model=_llm_assistant.default_model,
                messages=[{"role": "user", "content": "测试连接"}],
                max_tokens=5
            )
            print("✅ LLM助手初始化成功")
        except Exception as e:
            print(f"⚠️ LLM助手初始化失败: {e}")
            print("将使用传统判分模式")
            _llm_assistant = None
    
    return _llm_assistant