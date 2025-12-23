import os
import json
import re
import requests

from graph_loader import load_knowledge_graph
from graph_queries import *

# ======================================================
# LOAD KNOWLEDGE GRAPH
# ======================================================
G = load_knowledge_graph()

# ======================================================
# PERPLEXITY API SETUP
# ======================================================
API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not API_KEY:
    raise RuntimeError("PERPLEXITY_API_KEY not set")

URL = "https://api.perplexity.ai/chat/completions"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# ======================================================
# SYSTEM PROMPT FOR STRUCTURAL QUESTIONS
# ======================================================
SYSTEM_PROMPT = """
You are a query interpretation system for a ship Digital Twin.

Your task:
- Identify which graph query should be used
- Identify the target component

RULES:
- Influence or dependency → who_affects(component)
- Downstream effects → downstream_impact(component)

Available graph queries:
1. who_affects(component)
2. what_it_affects(component)
3. upstream_dependencies(component)
4. downstream_impact(component)

Return ONLY valid JSON:
{
  "query_type": "one_of_the_above",
  "component": "component_name"
}
"""

print("\n--- Natural Language Digital Twin Interface ---\n")
print("Ask a question about the ship refrigeration system.\n")

# ======================================================
# MAIN LOOP
# ======================================================
while True:
    user_question = input("NL Question (or 'exit'): ").strip()

    if user_question.lower() == "exit":
        print("Exiting NL interface.")
        break

    q_lower = user_question.lower()

    # ======================================================
    # 1. WHY QUESTIONS → EXPLANATORY MODE
    # ======================================================
    if q_lower.startswith("why"):
        print("\nExplanatory question detected.")
        print("Switching to explanatory mode.\n")

        explain_payload = {
            "model": "sonar-pro",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a marine refrigeration expert. Explain using engineering principles."
                },
                {
                    "role": "user",
                    "content": user_question
                }
            ],
            "temperature": 0.2
        }

        response = requests.post(URL, headers=HEADERS, json=explain_payload)
        response.raise_for_status()

        explanation = response.json()["choices"][0]["message"]["content"]
        print(explanation)
        print("\n----------------------------------\n")
        continue

    # ======================================================
    # 2. FAULT-IMPACT QUESTIONS
    # ======================================================
    if q_lower.startswith("what happens if"):
        print("\nFault-impact question detected.")
        print("Routing to downstream impact analysis.\n")

        raw_component = (
            q_lower.replace("what happens if", "")
            .replace("trips", "")
            .replace("trip", "")
            .strip()
            .rstrip("?")
        )

        # Normalize component name using token matching against KG nodes
        component = None
        raw_tokens = set(raw_component.replace("the ", "").split())

        for node in G.nodes:
            node_tokens = set(node.lower().split())
            if raw_tokens.issubset(node_tokens):
                component = node
                break

        if component is None:
            print("Component not found in Knowledge Graph.")
            print("\n----------------------------------\n")
            continue

        print(f"→ Interpreted as: downstream_impact('{component}')\n")

        try:
            results = downstream_impact(G, component)
            print("Answer:")
            if not results:
                print(" - No downstream impact found.")
            else:
                for r in results:
                    print(f" - {r}")
        except ValueError:
            print("Component not found in Knowledge Graph.")

        print("\n----------------------------------\n")
        continue

    # ======================================================
    # 3. CONTROL-LOGIC QUESTIONS (START / STOP)
    # ======================================================
    control_keywords = ["stop", "start", "cut out", "cut-out", "safety"]

    if any(word in q_lower for word in control_keywords):
        print("\nControl-logic question detected.")
        print("Routing directly to Knowledge Graph.\n")

        component = "compressor"
        results = who_affects(G, component)

        print(f"→ Interpreted as: who_affects('{component}')\n")
        print("Answer:")
        for r in results:
            print(f" - {r}")

        print("\n----------------------------------\n")
        continue

    # ======================================================
    # 4. STRUCTURAL QUESTIONS → LLM INTENT EXTRACTION
    # ======================================================
    intent_payload = {
        "model": "sonar-pro",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_question}
        ],
        "temperature": 0
    }

    response = requests.post(URL, headers=HEADERS, json=intent_payload)
    response.raise_for_status()

    intent_text = response.json()["choices"][0]["message"]["content"]
    intent_text = re.sub(r"```json|```", "", intent_text).strip()

    try:
        intent = json.loads(intent_text)
    except json.JSONDecodeError:
        print("\nCould not map this question to a structured graph query.")
        print("Not supported in this version.")
        print("\n----------------------------------\n")
        continue

    if "query_type" not in intent or "component" not in intent:
        print("\nIncomplete intent detected.")
        print("Cannot resolve to a single graph query.")
        print("\n----------------------------------\n")
        continue

    query_type = intent["query_type"].split("(")[0].strip()
    component = intent["component"]

    print(f"\n→ Interpreted as: {query_type}('{component}')\n")

    # ======================================================
    # 5. KNOWLEDGE GRAPH REASONING
    # ======================================================
    try:
        if query_type == "who_affects":
            results = who_affects(G, component)
        elif query_type == "what_it_affects":
            results = what_it_affects(G, component)
        elif query_type == "upstream_dependencies":
            results = upstream_dependencies(G, component)
        elif query_type == "downstream_impact":
            results = downstream_impact(G, component)
        else:
            print("Unknown query type.")
            print("\n----------------------------------\n")
            continue

        print("Answer:")
        if not results:
            print(" - No structural dependencies found.")
        else:
            for r in results:
                print(f" - {r}")

    except ValueError:
        print("\nComponent not found in Knowledge Graph.")
        print("This question cannot be answered structurally.")

    print("\n----------------------------------\n")
