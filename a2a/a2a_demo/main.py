import argparse, os, datetime, sys
from .bus import MessageBus
from .agents.base import Message
from .agents.researcher import ResearcherAgent
from .agents.writer import WriterAgent
from .agents.supervisor import Supervisor

def cli():
    parser = argparse.ArgumentParser(description="A2A Collaboration Demo (pure Python)")
    parser.add_argument("--task", type=str, required=True, help="High-level task for the agents to complete")
    parser.add_argument("--data-dir", type=str, default=os.path.join(os.path.dirname(__file__), "..", "data", "docs"))
    parser.add_argument("--max-turns", type=int, default=8)
    parser.add_argument("--output-dir", type=str, default="./output")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    bus = MessageBus()
    researcher = ResearcherAgent(bus=bus, data_dir=args.data_dir)
    writer = WriterAgent(bus=bus, min_sections=3)
    supervisor = Supervisor(bus=bus, task=args.task, max_turns=args.max_turns)

    # Kick off
    msg = supervisor.bootstrap()
    bus.publish(msg)

    final_report = None

    # Event loop
    for step in range(args.max_turns * 3):
        # dispatch to recipients in simple round-robin
        for agent in (researcher, writer, supervisor):
            last = bus.transcript()[-1]
            reply = agent.receive(last)
            if reply is not None:
                bus.publish(reply)
                # capture report
                if reply.role == "Writer" and reply.meta.get("is_final_candidate"):
                    final_report = reply.content
                if reply.meta.get("intent") == "stop":
                    # write transcript and report
                    save_outputs(bus, final_report, args.output_dir)
                    print("== Session finished ==")
                    return
    # Fallback
    save_outputs(bus, final_report, args.output_dir)
    print("== Session ended by loop guard ==")

def save_outputs(bus, final_report, outdir):
    ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    # transcript
    tpath = os.path.join(outdir, f"transcript-{ts}.txt")
    with open(tpath, "w", encoding="utf-8") as f:
        for m in bus.transcript():
            f.write(f"[{datetime.datetime.fromtimestamp(m.timestamp)}] {m.role}: {m.content}\n")
    print(f"Wrote transcript: {tpath}")
    if final_report:
        rpath = os.path.join(outdir, f"report-{ts}.md")
        with open(rpath, "w", encoding="utf-8") as f:
            f.write(final_report)
        print(f"Wrote report: {rpath}")
    else:
        print("No final report produced.")

if __name__ == "__main__":
    cli()
