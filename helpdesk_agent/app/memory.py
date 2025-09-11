from collections import defaultdict
_sessions = defaultdict(list)

def append_turn(session_id:str, role:str, text:str, meta=None):
    _sessions[session_id].append({"role": role, "text": text, "meta": meta or {}})

def get_history(session_id:str, k:int=8):
    return _sessions[session_id][-k:]
