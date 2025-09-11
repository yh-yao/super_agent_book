from workflows.edu_chain import EduChain

if __name__ == "__main__":
    student_id = "stu_001"
    answers = ["2", "Paris", "H2O"]
    keys = ["2", "Paris", "H2O"]

    chain = EduChain()
    result = chain.run(student_id, answers, keys)

    print("✅ 批改完成:", result["results"])
    print("📊 分数:", result["score"])
    print("📝 反馈:", result["feedback"])
