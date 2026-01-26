from llm.openai_llm import LLM
from skills.ppt_generation.skill import PPTGenerationSkill
from pathlib import Path

class Agent:
    """Agent：读取 Skill 描述，完成调度与执行"""

    def __init__(self):
        self.llm = LLM()
        self.skills = {
            "ppt_generation": {
                "instance": PPTGenerationSkill(),
                "spec": self._load_skill_md("skills/ppt_generation/SKILL.md")
            }
        }

    def _load_skill_md(self, path: str) -> str:
        return Path(path).read_text(encoding="utf-8")

    def run(self, user_input: str):
        ppt_ir = self.llm.generate_ppt_ir(user_input)

        assert "title" in ppt_ir
        assert "slides" in ppt_ir

        return self.skills["ppt_generation"]["instance"].run(
            title=ppt_ir["title"],
            slides=ppt_ir["slides"],
            output_path=f"{user_input}.pptx"
        )
