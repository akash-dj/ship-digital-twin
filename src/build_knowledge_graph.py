import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
import re

# ---------- Paths ----------
FACTS_PATH = Path("kg/raw_facts.json")

# ---------- Load & sanitize facts ----------
raw_text = FACTS_PATH.read_text(encoding="utf-8").strip()

# Remove markdown fences if present
raw_text = re.sub(r"```json|```", "", raw_text).strip()

# Extract JSON array only
json_start = raw_text.find("[")
json_end = raw_text.rfind("]") + 1

if json_start == -1 or json_end == -1:
    raise ValueError("No JSON array found in raw_facts.json")

facts = json.loads(raw_text[json_start:json_end])

# ---------- Create graph ----------
G = nx.DiGraph()

# ---------- Node classification ----------
HIGH_SIDE = {"Compressor", "Condenser"}
LOW_SIDE = {"Evaporator", "Valve", "Pipe"}
CONTROL = {"Controller", "Sensor"}

def node_color(node_class):
    if node_class in HIGH_SIDE:
        return "red"
    if node_class in LOW_SIDE:
        return "skyblue"
    if node_class in CONTROL:
        return "green"
    return "gray"

# ---------- Build graph ----------
for fact in facts:
    subj = fact["subject"]
    obj = fact["object"]

    subj_class = fact["subject_class"]
    obj_class = fact["object_class"]
    predicate = fact["predicate"]

    G.add_node(subj, category=subj_class, color=node_color(subj_class))
    G.add_node(obj, category=obj_class, color=node_color(obj_class))
    G.add_edge(subj, obj, label=predicate)

# ---------- Visualization ----------
plt.figure(figsize=(14, 10))
pos = nx.spring_layout(G, seed=42)

node_colors = [G.nodes[n]["color"] for n in G.nodes]

nx.draw(
    G,
    pos,
    with_labels=True,
    node_color=node_colors,
    node_size=2500,
    font_size=9,
    font_weight="bold",
    arrows=True
)

edge_labels = nx.get_edge_attributes(G, "label")
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)

plt.title("Ship Refrigeration System – Knowledge Graph")
plt.show()

print("STEP 4 complete: Knowledge Graph constructed and visualized.")
