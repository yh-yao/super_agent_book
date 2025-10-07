
from typing import List
from app.schemas import UserProfile

class Safety:
    def pre_check(self, text: str, user: UserProfile) -> List[str]:
        flags = []
        low = text.lower()
        if "password" in low or "apikey" in low:
            flags.append("pii:secret")
        if any(k in low for k in ["暴力", "仇恨", "违法"]):
            flags.append("safety:content_flag")
        return flags

    def mid_policy(self, tool_name: str, user: UserProfile) -> bool:
        if user.safety_tier == "strict" and tool_name in {"code_exec","shell"}:
            return False
        return True

    def post_guard(self, draft: str) -> str:
        return draft
