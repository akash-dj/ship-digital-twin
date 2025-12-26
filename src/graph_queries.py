import networkx as nx

def resolve_component(G, name):
    """
    Resolve NL component name to actual graph node.
    """
    name_norm = name.lower().replace("_", " ").strip()

    for node in G.nodes:
        if node.lower() == name_norm:
            return node

    raise ValueError(f"Component '{name}' not found in Knowledge Graph")

def who_affects(G, component):
    component = resolve_component(G, component)
    return [(u, G[u][component]["label"]) for u in G.predecessors(component)]

def what_it_affects(G, component):
    component = resolve_component(G, component)
    return [(v, G[component][v]["label"]) for v in G.successors(component)]

def upstream_dependencies(G, component):
    component = resolve_component(G, component)
    return list(nx.ancestors(G, component))

def downstream_impact(G, component):
    component = resolve_component(G, component)
    return list(nx.descendants(G, component))
