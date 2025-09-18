"""
动态题目生成器：使用LLM根据学生的学习情况生成个性化题目
"""
from __future__ import annotations
import json
import uuid
from typing import List, Optional
from .memory import StudentProfile
from .questions import Question
from .llm_assistant import get_llm_assistant

class QuestionGenerator:
    """动态题目生成器"""
    
    def __init__(self):
        self.llm_assistant = get_llm_assistant()
    
    def generate_personalized_question(
        self, 
        profile: StudentProfile, 
        target_skill: str,
        difficulty: float = 0.5
    ) -> Optional[Question]:
        """
        为特定技能生成个性化题目
        
        Args:
            profile: 学生档案
            target_skill: 目标技能标签 (如 "grammar:present-simple")
            difficulty: 题目难度 (0.0-1.0)
        """
        if not self.llm_assistant:
            return None
        
        # 分析学生的错误模式
        error_patterns = self._analyze_error_patterns(profile, target_skill)
        
        # 根据技能类型选择生成策略
        if target_skill.startswith("grammar:"):
            return self._generate_grammar_question(profile, target_skill, difficulty, error_patterns)
        elif target_skill.startswith("vocab:"):
            return self._generate_vocabulary_question(profile, target_skill, difficulty, error_patterns)
        else:
            return self._generate_general_question(profile, target_skill, difficulty, error_patterns)
    
    def _analyze_error_patterns(self, profile: StudentProfile, skill: str) -> List[str]:
        """分析学生在特定技能上的错误模式"""
        patterns = []
        
        # 从历史记录中找出该技能的错误题目
        skill_errors = [
            record for record in profile.history 
            if not record.is_correct and skill in record.tags
        ]
        
        if len(skill_errors) >= 2:
            patterns.append(f"在{skill}上有{len(skill_errors)}次错误")
        
        # 分析掌握度
        skill_stat = profile.skills.get(skill)
        if skill_stat and skill_stat.mastery < 0.3:
            patterns.append("掌握度很低，需要基础练习")
        elif skill_stat and skill_stat.mastery < 0.6:
            patterns.append("掌握度中等，需要巩固练习")
        
        return patterns
    
    def _generate_grammar_question(
        self, 
        profile: StudentProfile, 
        skill: str, 
        difficulty: float,
        error_patterns: List[str]
    ) -> Optional[Question]:
        """生成语法题目"""
        
        if not self.llm_assistant:
            return None
        
        grammar_type = skill.split(":")[-1]  # 如 "present-simple"
        
        prompt = f"""
作为英语题目生成专家，请为{profile.level}等级学生生成一道{grammar_type}语法题。

学生信息：
- 等级: {profile.level}
- 错误模式: {'; '.join(error_patterns) if error_patterns else '无特别错误模式'}
- 目标难度: {difficulty:.1f} (0.0=简单, 1.0=困难)

要求：
1. 生成选择题（4个选项）
2. 题目要针对{grammar_type}语法点
3. 难度适合{profile.level}等级
4. 包含详细的解释

请返回JSON格式：
{{
    "stem": "题干内容",
    "options": ["选项1", "选项2", "选项3", "选项4"],
    "answer": 正确选项索引(0-3),
    "explain": "详细解释",
    "difficulty": 实际难度(0.0-1.0)
}}
"""
        
        try:
            response = self.llm_assistant.client.chat.completions.create(
                model=self.llm_assistant.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                return None
                
            data = json.loads(content)
            
            # 创建Question对象
            question = Question(
                id=f"generated_{uuid.uuid4().hex[:8]}",
                stem=data["stem"],
                options=data["options"],
                answer=data["answer"],
                explain=data["explain"],
                cefr=profile.level,
                tags=[skill],
                difficulty=data.get("difficulty", difficulty)
            )
            
            return question
            
        except Exception as e:
            print(f"语法题目生成失败: {e}")
            return None
    
    def _generate_vocabulary_question(
        self, 
        profile: StudentProfile, 
        skill: str, 
        difficulty: float,
        error_patterns: List[str]
    ) -> Optional[Question]:
        """生成词汇题目"""
        
        if not self.llm_assistant:
            return None
        
        vocab_type = skill.split(":")[-1]  # 如 "daily"
        
        prompt = f"""
作为英语题目生成专家，请为{profile.level}等级学生生成一道{vocab_type}词汇题。

学生信息：
- 等级: {profile.level}
- 错误模式: {'; '.join(error_patterns) if error_patterns else '无特别错误模式'}
- 目标难度: {difficulty:.1f}

要求：
1. 可以是选择题或填空题
2. 词汇主题: {vocab_type}
3. 适合{profile.level}等级
4. 实用性强

请返回JSON格式：
{{
    "stem": "题干内容",
    "options": ["选项1", "选项2", "选项3", "选项4"] or null,
    "answer": 选项索引或填空答案,
    "explain": "详细解释",
    "difficulty": 实际难度(0.0-1.0)
}}
"""
        
        try:
            response = self.llm_assistant.client.chat.completions.create(
                model=self.llm_assistant.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                return None
                
            data = json.loads(content)
            
            question = Question(
                id=f"generated_{uuid.uuid4().hex[:8]}",
                stem=data["stem"],
                options=data.get("options"),
                answer=data["answer"],
                explain=data["explain"],
                cefr=profile.level,
                tags=[skill],
                difficulty=data.get("difficulty", difficulty)
            )
            
            return question
            
        except Exception as e:
            print(f"词汇题目生成失败: {e}")
            return None
    
    def _generate_general_question(
        self, 
        profile: StudentProfile, 
        skill: str, 
        difficulty: float,
        error_patterns: List[str]
    ) -> Optional[Question]:
        """生成通用题目"""
        
        if not self.llm_assistant:
            return None
        
        prompt = f"""
作为英语题目生成专家，请为{profile.level}等级学生生成一道{skill}技能的题目。

学生信息：
- 等级: {profile.level}
- 技能点: {skill}
- 错误模式: {'; '.join(error_patterns) if error_patterns else '无特别错误模式'}
- 目标难度: {difficulty:.1f}

请生成适合的题目类型（选择题或开放题），确保：
1. 针对{skill}技能点
2. 适合{profile.level}等级
3. 有教育价值

请返回JSON格式：
{{
    "stem": "题干内容",
    "options": 选项数组或null,
    "answer": 答案,
    "explain": "详细解释",
    "difficulty": 实际难度(0.0-1.0)
}}
"""
        
        try:
            response = self.llm_assistant.client.chat.completions.create(
                model=self.llm_assistant.default_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                return None
                
            data = json.loads(content)
            
            question = Question(
                id=f"generated_{uuid.uuid4().hex[:8]}",
                stem=data["stem"],
                options=data.get("options"),
                answer=data["answer"],
                explain=data["explain"],
                cefr=profile.level,
                tags=[skill],
                difficulty=data.get("difficulty", difficulty)
            )
            
            return question
            
        except Exception as e:
            print(f"通用题目生成失败: {e}")
            return None
    
    def generate_weakness_focused_questions(
        self, 
        profile: StudentProfile, 
        count: int = 3
    ) -> List[Question]:
        """
        为学生的薄弱技能生成多道针对性题目
        
        Args:
            profile: 学生档案
            count: 生成题目数量
        """
        questions = []
        
        if not self.llm_assistant:
            return questions
        
        # 找出掌握度最低的几个技能
        weak_skills = sorted(
            profile.skills.items(), 
            key=lambda x: x[1].mastery
        )[:count]
        
        for skill, stat in weak_skills:
            # 根据掌握度调整难度
            difficulty = max(0.1, min(0.8, stat.mastery + 0.1))
            
            question = self.generate_personalized_question(
                profile, skill, difficulty
            )
            
            if question:
                questions.append(question)
        
        return questions

# 全局题目生成器实例
_question_generator = None

def get_question_generator() -> Optional[QuestionGenerator]:
    """获取题目生成器实例"""
    global _question_generator
    
    if _question_generator is None:
        _question_generator = QuestionGenerator()
    
    return _question_generator