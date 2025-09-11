from workflows.bi_chain import BIChain

if __name__ == "__main__":
    chain = BIChain()
    result = chain.run("market_data.csv")
    print("✅ 报告生成完成:", result)
