from graph_loader import load_knowledge_graph
from graph_queries import *

G = load_knowledge_graph()

print("\n--- Digital Twin Query Engine ---\n")

print("Available queries:")
print("1. Who affects a component?")
print("2. What does a component affect?")
print("3. Show upstream dependencies")
print("4. Show downstream impact")
print("5. Exit")

while True:
    choice = input("\nSelect query (1-5): ")

    if choice == "5":
        print("Exiting query engine.")
        break

    component = input("Enter component name exactly as in graph: ")

    if choice == "1":
        results = who_affects(G, component)
        print(f"\nComponents affecting '{component}':")
        for r in results:
            print(f" - {r[0]} ({r[1]})")

    elif choice == "2":
        results = what_it_affects(G, component)
        print(f"\nComponents affected by '{component}':")
        for r in results:
            print(f" - {r[0]} ({r[1]})")

    elif choice == "3":
        results = upstream_dependencies(G, component)
        print(f"\nUpstream dependencies of '{component}':")
        for r in results:
            print(f" - {r}")

    elif choice == "4":
        results = downstream_impact(G, component)
        print(f"\nDownstream impact of '{component}':")
        for r in results:
            print(f" - {r}")

    else:
        print("Invalid option.")
