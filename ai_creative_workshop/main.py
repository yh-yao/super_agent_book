from workflows.creative_chain import CreativeChain

if __name__ == "__main__":
    product = "夏日柠檬饮料"
    audience = "年轻人"
    creative_chain = CreativeChain()

    text, img = creative_chain.run(product, audience)

    with open("outputs/campaign.txt", "w", encoding="utf-8") as f:
        f.write(text)

    print("✅ 最终文案:", text)
    print("🎨 生成海报:", img)
