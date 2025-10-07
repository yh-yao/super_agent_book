from workflows.creative_chain import CreativeChain
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Creative Campaign Generator")
    parser.add_argument("--product", type=str, required=True, help="产品名称")
    parser.add_argument("--audience", type=str, required=True, help="目标受众")
    args = parser.parse_args()

    creative_chain = CreativeChain()
    text, img = creative_chain.run(args.product, args.audience)

    with open("outputs/campaign.txt", "w", encoding="utf-8") as f:
        f.write(text)

