from __future__ import annotations
from typing import Dict, List, Optional, Any
import json
from pathlib import Path
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

# 学生记忆与自适应学习系统
# 结合IRT（项目反应理论）和SM-2（间隔重复）算法思想实现个性化学习

class SkillStat(BaseModel):
    """技能统计信息"""
    correct: int = 0           # 正确次数
    wrong: int = 0             # 错误次数
    mastery: float = 0.0       # 掌握度 (0~1)
    difficulty_bias: float = 0.0  # 对该技能的个人难度偏差估计
    next_review: Optional[str] = None  # 下次复习时间 (ISO格式)

    def update(self, is_correct: bool, q_difficulty: float):
        """根据答题结果更新技能统计"""
        if is_correct:
            self.correct += 1
        else:
            self.wrong += 1

        # 使用指数加权移动平均更新掌握度
        alpha = 0.2  # 学习率
        target = 1.0 if is_correct else 0.0
        self.mastery = (1 - alpha) * self.mastery + alpha * target

        # 更新个人难度偏差：做对降低偏差，做错提高偏差
        self.difficulty_bias += (0.1 if not is_correct else -0.05) * (q_difficulty - 0.5)

        # 计算下次复习间隔（基于掌握度的间隔重复算法）
        base_days = 1 + 6 * self.mastery  # 掌握度越高，间隔越长
        # 错题时缩短复习间隔
        if not is_correct:
            base_days = max(0.5, base_days * 0.5)
        next_time = datetime.utcnow() + timedelta(days=base_days)
        self.next_review = next_time.isoformat(timespec="seconds")
class SkillStat(BaseModel):
    correct: int = 0
    wrong: int = 0
    mastery: float = 0.0        # 0~1
    difficulty_bias: float = 0.0  # 对该技能的难度偏差估计
    next_review: Optional[str] = None  # ISO 时间

    def update(self, is_correct: bool, q_difficulty: float):
        if is_correct:
            self.correct += 1
        else:
            self.wrong += 1

        # 简单掌握度估计（指数滑动）
        alpha = 0.2
        target = 1.0 if is_correct else 0.0
        self.mastery = (1 - alpha) * self.mastery + alpha * target

        # 学生对该技能的“难度偏差”：做对就降低偏差，做错则提高
        self.difficulty_bias += (0.1 if not is_correct else -0.05) * (q_difficulty - 0.5)

        # 复习间隔（掌握度越高，间隔越长）
        base_days = 1 + 6 * self.mastery
        # 错题时拉近
        if not is_correct:
            base_days = max(0.5, base_days * 0.5)
        next_time = datetime.utcnow() + timedelta(days=base_days)
        self.next_review = next_time.isoformat(timespec="seconds")

class QARecord(BaseModel):
    """答题记录"""
    qid: str                    # 题目ID
    ts: str                     # 答题时间戳
    is_correct: bool            # 是否正确
    cefr: str                   # CEFR等级
    tags: List[str]             # 技能标签
    difficulty: float           # 题目难度
    user_answer: Any            # 用户答案
    correct_answer: Any         # 正确答案

class StudentProfile(BaseModel):
    """学生档案"""
    user_id: str                # 用户ID
    name: str                   # 姓名
    level: str = "A1"           # 当前推断的CEFR等级
    skills: Dict[str, SkillStat] = Field(default_factory=dict)  # 技能统计 (key=标签)
    history: List[QARecord] = Field(default_factory=list)       # 答题历史

    def update_level(self):
        """根据技能掌握度更新CEFR等级"""
        if not self.skills:
            self.level = "A1"
            return
        
        # 使用掌握度中位数映射到CEFR等级
        mastery_vals = sorted([s.mastery for s in self.skills.values()])
        med = mastery_vals[len(mastery_vals)//2]
        
        if med < 0.3:
            self.level = "A1"
        elif med < 0.5:
            self.level = "A2"
        elif med < 0.65:
            self.level = "B1"
        elif med < 0.8:
            self.level = "B2"
        else:
            self.level = "C1"

class MemoryDB:
    """学生记忆数据库 - 负责持久化存储学生档案和学习历史"""
    
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"students": {}})

    def _read(self) -> dict:
        """读取数据库文件"""
        return json.loads(self.path.read_text(encoding="utf-8"))

    def _write(self, data: dict):
        """写入数据库文件"""
        self.path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_student(self, user_id: str, name: Optional[str] = None) -> StudentProfile:
        """获取或创建学生档案"""
        data = self._read()
        students = data.setdefault("students", {})
        if user_id not in students:
            students[user_id] = StudentProfile(user_id=user_id, name=name or user_id).model_dump()
            self._write(data)
        return StudentProfile(**students[user_id])

    def save_student(self, profile: StudentProfile):
        """保存学生档案"""
        data = self._read()
        data["students"][profile.user_id] = profile.model_dump()
        self._write(data)

    def log_interaction(self, profile: StudentProfile, record: QARecord):
        """记录学习交互并更新技能统计"""
        profile.history.append(record)
        
        # 更新每个技能标签的统计信息
        for tag in record.tags:
            stat = profile.skills.get(tag, SkillStat())
            stat.update(record.is_correct, record.difficulty)
            profile.skills[tag] = stat
            
        # 重新评估学生的CEFR等级
        profile.update_level()
        self.save_student(profile)
