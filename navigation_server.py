from flask import Flask, request, jsonify
import numpy as np
import tcod
from tsp_solver.greedy import solve_tsp

app = Flask(__name__)

# Your store matrix and functions from the template
store = np.array([
    [1,1,1,1,1,1,1,1],
    [1,1,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,1,1],
    [1,1,1,1,1,1,1,1],
    [1,1,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,1,1],
    [1,1,1,1,1,1,1,1],
    [1,1,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,1,1],
    [1,1,1,1,1,1,1,1]
], dtype=np.int64)

def get_distance(start_node: np.array, stop_node: np.array):
    cardinal_dir = [
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0]
    ]
    graph = tcod.path.CustomGraph(store.shape)
    graph.add_edges(edge_map=cardinal_dir, cost=store)
    pf = tcod.path.Pathfinder(graph)
    pf.add_root(start_node)
    pf.resolve()
    dist = pf.distance
    return dist[stop_node[0]][stop_node[1]]

# Web Service to compute the shortest path between nodes
@app.route('/shortest-path', methods=['POST'])
def shortest_path():
    # Parse input JSON data
    data = request.get_json()
    waypoints = data.get('waypoints', [])
    
    # Validate the input
    if not waypoints or len(waypoints) < 2:
        return jsonify({"error": "At least 2 waypoints are required"}), 400
    
    # Convert the waypoints into np.array
    nodes = [np.array([wp['x'], wp['y']]) for wp in waypoints]
    
    # Prepare the start and stop nodes (dummy example, can be modified)
    start_node = np.array([0, 0])
    
    # Append start node and reorganize node list
    my_nodes = np.array([start_node])
    my_nodes = np.append(my_nodes, nodes, axis=0)
    
    # Initialize the distance graph
    num_nodes = len(my_nodes)
    distance_graph = np.full((num_nodes, num_nodes), np.inf)
    
    # Calculate distance between all nodes
    for i in range(num_nodes):
        for j in range(num_nodes):
            if i == j:
                distance_graph[i][j] = 0
            else:
                distance_graph[i][j] = get_distance(my_nodes[i], my_nodes[j])
    
    # Solve the TSP problem
    solution = solve_tsp(distance_graph, endpoints=(0, 1))
    
    # Format the result
    result = {
        "order": solution,  # The order in which to visit the nodes
        "waypoints": [waypoints[i - 1] for i in solution if i != 0]  # Exclude the dummy start node
    }
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
