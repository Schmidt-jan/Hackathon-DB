from tsp_solver.greedy import solve_tsp
import numpy as np
import tcod
import time

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
UP = 0b1
DOWN = 0b10
LEFT = 0b100
RIGHT = 0b1000
NONE = 0b0
counter = 0

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

def get_direction(desired, my_loc):
    cardinal_dir = [
                    [0,1,0],
                    [1,0,1],
                    [0,1,0]
                   ]
    graph = tcod.path.CustomGraph(store.shape)
    graph.add_edges(edge_map = cardinal_dir, cost=store)
    pf = tcod.path.Pathfinder(graph)
    pf.add_root(my_loc)
    pf.resolve()
    i : int = 0
    next_loc = pf.path_to((desired[0],desired[1]))[i]
    while (next_loc == my_loc).all():
        i += 1
        if i == len(pf.path_to((desired[0], desired[1]))):
            break
        next_loc = pf.path_to((desired[0], desired[1]))[i]
    ret = 0
    if next_loc[0] > my_loc[0]:
        ret = RIGHT
    elif next_loc[0] < my_loc[0]:
        ret = LEFT
    elif next_loc[1] > my_loc[1]:
        ret = UP
    elif next_loc[1] < my_loc[1]:
        ret = DOWN
    else:
        ret = NONE
    print(next_loc)
    return ret

def got_item():
    if counter % 15 == 14:
        return True
    return False

def get_initial_path(nodes, my_loc):
    # plus 2 for start and stop nodes.
    distance_graph : list #list(list(double))
    distance_graph = np.array([[np.inf]*(len(nodes) + 2)] * (len(nodes) + 2))
    # Node 1,2 are start/stop nodes last node is dummy node to make sure we have start/stop

    start_node : np.array
    start_node = np.array(my_loc) # np.array([0,0])

    my_nodes : np.array
    my_nodes= np.array([start_node, np.array([0,0])])
    my_nodes = np.append(my_nodes,nodes)
    my_nodes = my_nodes.reshape(-1,2)

    i : int = 0
    j : int = 0
    for i in range(0,len(distance_graph)):
        for j in range(0,len(distance_graph) ):
            if i == j:
                distance_graph[i][j] = 0
            else:
                distance_graph[i][j] = get_distance(my_nodes[i], my_nodes[j])
    sol = solve_tsp(distance_graph, endpoints=(0,1))
    return sol


def main():
    global counter
    nodes : [list] = [[0,2],[2,3],[4,4]]
    my_loc = [0,0]
    desired_path = get_initial_path(nodes, my_loc)
    while True:
        print(my_loc)
        direc = get_direction(nodes[desired_path[0]], my_loc)
        if direc == UP:
            my_loc[1] = my_loc[1] + 1
        elif direc == DOWN:
            my_loc[1] = my_loc[1] - 1
        elif direc == LEFT:
            my_loc[0] = my_loc[0] - 1
        elif direc == RIGHT:
            my_loc[0] = my_loc[0] + 1
        time.sleep(1)
        if got_item():
            nodes = nodes[1:]
            if len(nodes) == 0:
                break;
        get_initial_path(nodes, my_loc)
        counter += 1
        if counter == 25:
            break;

if __name__ == '__main__':
    main()
