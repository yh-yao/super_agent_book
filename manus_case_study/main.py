from workflows.manus_chain import ManusChain

if __name__ == "__main__":
    chain = ManusChain()
    result = chain.run("分析特斯拉 Q2 财报")
    print("✅ 任务完成，报告已生成：outputs/report.md")
