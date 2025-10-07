from __future__ import annotations
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
import random
from pydantic import BaseModel

class Question(BaseModel):
    """题目数据结构"""
    id: str                               # 题目唯一标识
    stem: str                             # 题干（可包含 {placeholder} 占位符）
    options: Optional[List[str]] = None   # 选择题选项（None表示开放题）
    answer: Any                           # 正确答案（字符串或选项索引）
    explain: Optional[str] = None         # 题目解释
    cefr: str                             # CEFR等级
    tags: List[str]                       # 技能标签（与课程大纲对应）
    difficulty: float                     # 题目难度 (0.0~1.0)

class QuestionBank(BaseModel):
    """题库管理器"""
    by_id: Dict[str, Question]

    @staticmethod
    def load(path: Path) -> "QuestionBank":
        """从JSON文件加载题库"""
        data = json.loads(path.read_text(encoding="utf-8"))
        by_id = {q["id"]: Question(**q) for q in data["questions"]}
        return QuestionBank(by_id=by_id)

    def filter(
        self,
        cefr: Optional[str] = None,
        tags: Optional[List[str]] = None,
        difficulty_range: Optional[tuple] = None
    ) -> List[Question]:
        """
        根据条件筛选题目
        
        Args:
            cefr: CEFR等级筛选
            tags: 技能标签筛选（包含任一标签即可）
            difficulty_range: 难度区间筛选 (min, max)
        """
        qs = list(self.by_id.values())
        
        if cefr:
            qs = [q for q in qs if q.cefr.upper() == cefr.upper()]
            
        if tags:
            tag_set = set(tags)
            qs = [q for q in qs if tag_set.intersection(q.tags)]
            
        if difficulty_range:
            lo, hi = difficulty_range
            qs = [q for q in qs if lo <= q.difficulty <= hi]
            
        return qs

    def sample(self, **kwargs) -> Optional[Question]:
        """从筛选后的题目中随机选择一道"""
        pool = self.filter(**kwargs)
        return random.choice(pool) if pool else None
