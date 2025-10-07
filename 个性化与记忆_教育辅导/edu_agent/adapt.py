from __future__ import annotations
from typing import List, Optional, Tuple
import random
from .memory import StudentProfile, SkillStat
from .questions import QuestionBank, Question
from .question_generator import get_question_generator

class AdaptivePolicy:
    """
    自适应出题策略：
    - 60% 复习已学内容（优先到期复习和低掌握度的技能）
    - 40% 探索新知识（邻接主题或当前CEFR等级内容）
    - 难度调整：根据个人掌握度和难度偏差确定适合的难度区间
    """
    def __init__(self, review_ratio: float = 0.6):
        self.review_ratio = review_ratio

    def target_difficulty_window(self, mastery: float, bias: float) -> Tuple[float, float]:
        """
        计算适合学生的题目难度区间
        
        Args:
            mastery: 技能掌握度 (0-1)
            bias: 个人难度偏差
            
        Returns:
            (min_difficulty, max_difficulty) 难度区间
        """
        # 基于掌握度调整难度：掌握度高 -> 适当提升难度；掌握度低 -> 降低难度
        center = 0.5 + (mastery - 0.5) * 0.4 - bias
        width = 0.25 - 0.1 * abs(mastery - 0.5)  # 掌握度极端时缩小难度区间
        
        lo = max(0.0, center - width)
        hi = min(1.0, center + width)
        return lo, hi

    def pick_tags_for_review(self, profile: StudentProfile, k: int = 1) -> List[str]:
        """
        选择需要复习的技能标签
        优先选择掌握度低或有到期复习计划的技能
        """
        pairs = []
        for tag, stat in profile.skills.items():
            # 评分：掌握度越低分数越高，有到期复习的加分
            score = (1 - stat.mastery) + (0.2 if stat.next_review else 0.0)
            pairs.append((score, tag))
        
        pairs.sort(reverse=True)
        return [t for _, t in pairs[:k]] if pairs else []

    def select_question(self, bank: QuestionBank, profile: StudentProfile) -> Optional[Question]:
        """
        自适应选择题目：根据学习策略和学生档案选择最适合的题目
        优先尝试动态生成，然后降级到题库选择
        """
        rnd = random.random()
        
        # 复习模式：选择需要复习的技能对应题目
        if rnd < self.review_ratio and profile.skills:
            tags = self.pick_tags_for_review(profile, k=2) or list(profile.skills.keys())
            tag = random.choice(tags)
            stat = profile.skills.get(tag, SkillStat())
            lo, hi = self.target_difficulty_window(stat.mastery, stat.difficulty_bias)
            
            # 尝试动态生成针对性题目
            generator = get_question_generator()
            if generator and stat.mastery < 0.6:  # 只对掌握度较低的技能生成题目
                difficulty = (lo + hi) / 2  # 使用难度区间的中值
                generated_q = generator.generate_personalized_question(profile, tag, difficulty)
                if generated_q:
                    return generated_q
            
            # 降级到题库选择
            q = bank.sample(tags=[tag], difficulty_range=(lo, hi))
            if q: 
                return q

        # 探索模式：选择当前CEFR等级的新题目
        cefr = profile.level
        q = bank.sample(cefr=cefr)
        return q
