from collections import defaultdict

_sessions = defaultdict(list)

def append_turn(session_id:str, role:str, text:str):
    _sessions[session_id].append({"role": role, "text": text})

def get_history(session_id:str, k:int=6):
    history = _sessions[session_id][-k:]
    return "\n".join([f"{h['role']}: {h['text']}" for h in history])
