import networkx as nx
import math
def create_activity_network(activities, predecessors, times):
    G = nx.DiGraph()
    nodes = {}
    common_start_node = 0
    next_free_node = 1
    last_end_node = None
    for i, activity in enumerate(activities):
        preds = predecessors[i]
        te = times[activity]
        if not preds:
            # No predecessors: Connect to common start node
            end_node = next_free_node
            next_free_node += 1
            G.add_edge(common_start_node, end_node, label=f"{activity} ({te:.2f})", weight=te)
            nodes[activity] = (common_start_node, end_node)
        else:
            # Create shared start node based on predecessors
            shared_start_node = None
            for pred in preds:
                pred_end_node = nodes[pred][1]
                if shared_start_node is None:
                    shared_start_node = pred_end_node
                else:
                    G.add_edge(pred_end_node, shared_start_node, label="", weight=0)
            # Determine end node logic
            if i == len(activities) - 2:
                end_node = next_free_node
                next_free_node += 1
                last_end_node = end_node
            elif i == len(activities) - 1:
                end_node = last_end_node
            else:
                end_node = next_free_node
                next_free_node += 1
            G.add_edge(shared_start_node, end_node, label=f"{activity} ({te:.2f})", weight=te)
            nodes[activity] = (shared_start_node, end_node)
    return G, nodes
def calculate_critical_path(G):
    # Earliest Start Times (E)
    E = {node: 0 for node in G.nodes}
    topo_order = list(nx.topological_sort(G))
    for node in topo_order:
        for neighbor in G.neighbors(node):
            edge_weight = G[node][neighbor]['weight']
            E[neighbor] = max(E[neighbor], E[node] + edge_weight)
    # Latest Start Times (L)
    L = {node: float('inf') for node in G.nodes}
    end_node = max(E, key=E.get)
    L[end_node] = E[end_node]
    for node in reversed(topo_order):
        for neighbor in G.neighbors(node):
            edge_weight = G[node][neighbor]['weight']
            L[node] = min(L[node], L[neighbor] - edge_weight)
    # Critical Path Identification
    critical_path = []
    for u, v in G.edges:
        edge_slack = L[v] - E[u] - G[u][v]['weight']
        if edge_slack == 0:
            critical_path.append((u, v))
    return E, L, critical_path
def calculate_sigma_for_critical_path(critical_path, nodes, activity_details):
    sigma_squared_sum = 0
    critical_activities = []
    # Extract activities on the critical path
    for u, v in critical_path:
        for activity, (start, end) in nodes.items():
            if start == u and end == v:
                critical_activities.append(activity)
    # Compute sigma^2 for each activity
    for activity in critical_activities:
        o_time = activity_details[activity]['optimistic']
        p_time = activity_details[activity]['pessimistic']
        sigma_squared = ((p_time - o_time) / 6) ** 2
        sigma_squared_sum += sigma_squared
    # Calculate sigma for the critical path
    sigma = math.sqrt(sigma_squared_sum)
    return sigma, critical_activities
