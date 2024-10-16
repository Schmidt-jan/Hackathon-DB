from tsp_solver.greedy import solve_tsp
import numpy as np
import tcod
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import shortest_path

store : np.array = np.array([
                             [1,1,1,1,1,1,1,1],
                             [1,1,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,1,1],
                             [1,1,1,1,1,1,1,1],
                             [1,1,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,1,1],
                             [1,1,1,1,1,1,1,1],
                             [1,1,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,np.iinfo(np.int64).max,1,1],
                             [1,1,1,1,1,1,1,1]
                            ], dtype=np.int64
                           )

def get_distance(start_node: np.array, stop_node: np.array):
    cardinal_dir = [
                    [0,1,0],
                    [1,0,1],
                    [0,1,0]
                   ]
    graph = tcod.path.CustomGraph(store.shape)
    graph.add_edges(edge_map = cardinal_dir, cost=store)
    pf = tcod.path.Pathfinder(graph)
    pf.add_root(start_node)
    pf.resolve()
    dist = pf.distance
    return dist[stop_node[0]][stop_node[1]]

def main():
    nodes : [list] = [[0,2],[2,3],[4,4]]

    # plus 2 for start and stop nodes.
    # if something doesn't get filled just make it unreachable this is because we have
    # dummy unreachable node that can only be reached by start and endpoint.
    distance_graph : list #list(list(double))
    distance_graph = np.array([[np.inf]*(len(nodes) + 2)] * (len(nodes) + 2))
    # Node 1,2 are start/stop nodes last node is dummy node to make sure we have start/stop

    start_node : np.array
    start_node = np.array([0,0])

    my_nodes : np.array
    my_nodes= np.array([start_node, np.array([0,0])])
    my_nodes = np.append(my_nodes,nodes)
    my_nodes = my_nodes.reshape(-1,2)

    #  Initial dikstra to find distance between each node with walls.
    #  start at 1 b/c node zero will be our dummy node to make sure we have
    #  correct start and end points.
    i : int = 0
    j : int = 0
    for i in range(0,len(distance_graph)):
        for j in range(0,len(distance_graph) ):
            if i == j:
                distance_graph[i][j] = 0
            else:
                distance_graph[i][j] = get_distance(my_nodes[i], my_nodes[j])
    sol = solve_tsp(distance_graph, endpoints=(0,1))
    print(sol)


if __name__ == '__main__':
    main()
