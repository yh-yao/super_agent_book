from agents.grader_agent import GraderAgent
from agents.feedback_agent import FeedbackAgent
from agents.record_agent import RecordAgent

class EduChain:
    def __init__(self):
        self.grader = GraderAgent()
        self.feedback = FeedbackAgent()
        self.record = RecordAgent()

    def run(self, student_id, answers, keys):
        score, results = self.grader.run(answers, keys)
        fb = self.feedback.run(results, score, len(keys))
        rec = self.record.run(student_id, score, fb)
        return {"score": score, "results": results, "feedback": fb, "record": rec}
