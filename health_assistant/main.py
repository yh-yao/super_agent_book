from workflows.health_chain import HealthChain

if __name__ == "__main__":
    chain = HealthChain()
    query = "我最近经常头痛，是否需要去做脑部检查？"
    result = chain.run(query)
    print("✅ 最终输出:", result)
