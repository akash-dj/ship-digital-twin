import json
import networkx as nx
from pathlib import Path
import re

# ---------- Load & sanitize facts ----------
FACTS_PATH = Path("kg/raw_facts.json")

raw_text = FACTS_PATH.read_text(encoding="utf-8").strip()
raw_text = re.sub(r"```json|```", "", raw_text).strip()

json_start = raw_text.find("[")
json_end = raw_text.rfind("]") + 1

facts = json.loads(raw_text[json_start:json_end])

# ---------- Build graph ----------
G = nx.DiGraph()

for fact in facts:
    G.add_edge(
        fact["subject"],
        fact["object"],
        label=fact["predicate"],
        subject_class=fact["subject_class"],
        object_class=fact["object_class"]
    )

# ---------- QUERY FUNCTIONS ----------

def components_triggering(target):
    """Who can trigger a given component?"""
    return [
        (u, G[u][target]["label"])
        for u in G.predecessors(target)
    ]

def components_controlled_by(controller):
    """What does a controller regulate or trigger?"""
    return [
        (v, G[controller][v]["label"])
        for v in G.successors(controller)
    ]

def shared_dependencies(component):
    """What upstream components affect this component?"""
    return list(nx.ancestors(G, component))

# ---------- DEMO QUERIES ----------

print("\n--- Digital Twin Reasoning Output ---\n")

TARGET = "compressor"

print(f"1. Components that can affect '{TARGET}':")
for comp, relation in components_triggering(TARGET):
    print(f" - {comp} ({relation})")

print(f"\n2. All upstream dependencies of '{TARGET}':")
for dep in shared_dependencies(TARGET):
    print(f" - {dep}")

CONTROLLER = "room thermostat"

print(f"\n3. What '{CONTROLLER}' controls:")
for comp, relation in components_controlled_by(CONTROLLER):
    print(f" - {comp} ({relation})")

print("\nSTEP 5 complete: Digital Twin reasoning successful.")
