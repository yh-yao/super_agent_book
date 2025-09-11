from workflows.contract_chain import ContractChain

if __name__ == "__main__":
    contract_text = "本合同未设争议解决条款。违约责任过重。"
    chain = ContractChain()
    result = chain.run(contract_text)
    for clause, suggestion in result:
        print("⚠️ 风险点:", clause)
        print("✅ 修改建议:", suggestion)
        print("-"*40)
