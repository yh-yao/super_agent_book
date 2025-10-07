import hashlib, re
from typing import Tuple

# Very basic PHI scrubbing (demo purposes)
NAME_RE = re.compile(r"[\u4e00-\u9fa5A-Za-z]{2,6}先生|[\u4e00-\u9fa5A-Za-z]{2,6}女士")
PHONE_RE = re.compile(r"\b\+?\d[\d\- ]{7,}\b")

def hash_user(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:16]

def scrub_phi(text: str) -> Tuple[str, bool]:
    flagged = False
    new_text = NAME_RE.sub("[姓名]", text)
    if new_text != text:
        flagged = True
    newer_text = PHONE_RE.sub("[电话]", new_text)
    if newer_text != new_text:
        flagged = True
    return newer_text, flagged
