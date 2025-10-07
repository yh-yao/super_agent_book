from __future__ import annotations
from typing import Dict, List, Optional
import json
from pathlib import Path
from pydantic import BaseModel

class SyllabusItem(BaseModel):
    """课程大纲项目"""
    id: str                     # 项目唯一标识
    title: str                  # 项目标题
    cefr: str                   # CEFR等级 (A1/A2/B1/B2/C1)
    tags: List[str]             # 技能标签，如 ["vocab", "grammar:present-simple"]
    prereq: List[str] = []      # 前置要求的项目ID列表

class Syllabus(BaseModel):
    """课程大纲管理器"""
    items: Dict[str, SyllabusItem]

    @staticmethod
    def load(path: Path) -> "Syllabus":
        """从JSON文件加载课程大纲"""
        data = json.loads(path.read_text(encoding="utf-8"))
        items = {it["id"]: SyllabusItem(**it) for it in data["items"]}
        return Syllabus(items=items)

    def items_by_level(self, cefr: str) -> List[SyllabusItem]:
        """获取指定CEFR等级的所有课程项目"""
        return [it for it in self.items.values() if it.cefr.upper() == cefr.upper()]

    def neighbors(self, item_id: str) -> List[SyllabusItem]:
        """获取同等级的相邻课程项目"""
        me = self.items[item_id]
        return [it for it in self.items.values() if it.cefr == me.cefr and it.id != item_id]
