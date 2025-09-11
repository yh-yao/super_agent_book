class MemoryAgent:
    def __init__(self):
        self.short_term = []
        self.long_term = []

    def add_event(self, event):
        self.short_term.append(event)
        if len(self.short_term) > 5:
            self.long_term.append(self.short_term.pop(0))

    def recall(self):
        return {"short_term": self.short_term, "long_term": self.long_term}
