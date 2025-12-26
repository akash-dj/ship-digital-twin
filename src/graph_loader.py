import json
import re
import networkx as nx
from pathlib import Path

FACTS_PATH = Path("kg/raw_facts.json")

def load_knowledge_graph():
    raw_text = FACTS_PATH.read_text(encoding="utf-8").strip()
    raw_text = re.sub(r"```json|```", "", raw_text).strip()

    json_start = raw_text.find("[")
    json_end = raw_text.rfind("]") + 1

    facts = json.loads(raw_text[json_start:json_end])

    G = nx.DiGraph()

    for fact in facts:
        G.add_edge(
            fact["subject"],
            fact["object"],
            label=fact["predicate"],
            subject_class=fact["subject_class"],
            object_class=fact["object_class"]
        )

    return G
