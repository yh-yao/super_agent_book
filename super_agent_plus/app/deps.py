
from core.intent import IntentDetector
from core.router import ModelRouter
from core.safety import Safety
from core.reflection import Reflector
from core.orchestrator import Orchestrator
from agents.planner import Planner
from agents.researcher import Researcher
from agents.writer import Writer
from agents.analyst import Analyst
from rag.indexer import build_demo_store
from rag.retriever import Retriever

intentor = IntentDetector()
router = ModelRouter()
safety = Safety()
reflector = Reflector()

vs = build_demo_store("data")
retriever = Retriever(vs)

researcher = Researcher()
researcher.attach_retriever(retriever)

agents = {
    "planner": Planner(router, safety),
    "researcher": researcher,
    "writer": Writer(),
    "analyst": Analyst(),
}

orch = Orchestrator(agents, safety, reflector)


from core.orchestrator_langgraph import build_graph
graph = build_graph(agents, reflector)
