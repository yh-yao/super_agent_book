import argparse, requests, json
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="http://127.0.0.1:8000")
    p.add_argument("--question", required=True)
    p.add_argument("--user_id", default="demo_user")
    args = p.parse_args()
    payload = {"user_id": args.user_id, "question": args.question}
    r = requests.post(args.host + "/ask", json=payload, timeout=60)
    print(json.dumps(r.json(), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
