import uuid
_FAKE_DB = {}

def create_or_update_ticket(user_id:str, issue:str, priority:str="normal", extra=None):
    tid = str(uuid.uuid4())[:8]
    _FAKE_DB[tid] = {"user": user_id, "issue": issue, "priority": priority, "status":"open", "extra": extra or {}}
    return {"ticket_id": tid, "status":"open"}

def get_ticket(ticket_id:str):
    return _FAKE_DB.get(ticket_id)
