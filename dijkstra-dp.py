'''
Algorithms and Data Structures Assignment 1
Name: Ooi Yu Zhang
'''

#################################
############ Imports ############
from math import inf
#################################
#################################

####################
#### Question 1 ####
####################

class Edge:
    '''
    A basic class representing Edges in Graphs
    '''
    def __init__(self, a, b, c, d) -> None:
        '''
        Constructor for the Edge class
        '''
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def __str__(self) -> None:
        '''
        Return string for the Edge class
        '''
        res = "(" + str(self.a) + ", " + str(self.b) + ", " + str(self.c) + ", " + str(self.d) + ")"
        return res

class Vertex:
    '''
    A basic class representing Vertices in Graphs
    '''
    def __init__(self, id) -> None:
        '''
        Constructor for the Vertex class
        '''
        # ID of the Vertex
        self.id = id
        # List of Edges connected to this Vertex
        self.edges = []
        # Variables used for traversing
        self.discovered = False
        self.visited = False
        # The previous Vertex of this Vertex for shortest time
        self.previous = None
        # Shortest time from source to this Vertex
        self.time = inf
        # Boolean for whether the location has a passenger
        self.hasPassenger = False
        # Indicates whether this Vertex is part of the layered portion of the graph
        self.layeredVertex = False

    def __str__(self) -> None:
        '''
        Return string for the Vertex class
        '''
        res = str(self.id) + " with edges ["
        i = 0
        while i < len(self.edges) - 1:
            res = res + str(self.edges[i]) + ", "
            i += 1
        res = res + str(self.edges[i])
        res = res + "]"
        return res

    def add_edge(self, edge) -> None:
        '''
        Adds an edge onto the vertex
        '''
        self.edges.append(edge)

class Graph:
    '''
    A basic class representing Graphs
    '''
    def __init__(self, stops, edges) -> None:
        '''
        Constructor for the Graph class
        '''
        # Find total number of vertices
        vertices_count = -1
        for (a,b,c,d) in edges:
            vertices_count = max(vertices_count, max(a,b))

        # Initialise number of vertices in the graph
        # If there are locations with passengers, double the vertex count for layered graph
        if stops:
            self.vertices = [None] * (2 * (vertices_count + 1))
            # Duplicate list of edges for layered graph
            edges = edges * 2
        else:
            self.vertices = [None] * (vertices_count + 1)

        # Initialise vertices in the graph
        for i in range(len(edges)):
            self.vertices[edges[i][0]] = Vertex(edges[i][0])
            self.vertices[edges[i][1]] = Vertex(edges[i][1])
            # If there are loactions with passengers, initialise another layer of the vertices to the graph
            if stops and i >= len(edges) / 2:
                self.vertices[edges[i][0] + vertices_count + 1] = Vertex(edges[i][0] + vertices_count + 1)
                self.vertices[edges[i][1] + vertices_count + 1] = Vertex(edges[i][1] + vertices_count + 1)

        # Check for nodes with passengers
        for i in stops:
            node = self.vertices[i]
            node.hasPassenger = True
            node = self.vertices[i + vertices_count + 1]
            node.hasPassenger = True

        # Initialise edges in the graph
        self.add_edges(edges, stops, vertices_count)

    def __str__(self) -> None:
        res = ""
        for v in self.vertices:
            res = res + "Vertex " + str(v) + "\n"
        return res

    def add_edges(self, edges, stops, vertices_count) -> None:
        '''
        Adds all given edges onto the graph
        '''
        for i in range(len(edges)):
            # If there are passengers in the locations in the graph, initialise edges for layered graph
            if stops and i >= len(edges) / 2:
                u = edges[i][0] + vertices_count + 1
                v = edges[i][1] + vertices_count + 1
                w = edges[i][2]
                x = edges[i][3]
                current_edge = Edge(u,v,w,x)
                current_vertex = self.vertices[u]
                current_vertex.add_edge(current_edge)
            else:
                u = edges[i][0]
                v = edges[i][1]
                w = edges[i][2]
                x = edges[i][3]
                current_edge = Edge(u,v,w,x)
                current_vertex = self.vertices[u]
                current_vertex.add_edge(current_edge)
                # If there is a passenger at the current Vertex and the Vertex does not have a layered Vertex
                if current_vertex.hasPassenger and not current_vertex.layeredVertex:
                    # Initialise edge from Vertex to its duplicate in the layered portion of the graph
                    layered_edge = Edge(u, u + vertices_count + 1, 0, 0)
                    current_vertex.add_edge(layered_edge)
                    current_vertex.layeredVertex = True


    def dijkstra(self, source_id, carpool) -> None:
        '''
            Function description: This function utilises Dijkstra's algorithm to find the shortest time that can be taken from the given source node to all other nodes in a graph.

            Approach description: A MinHeap is initialised which is used in Dijkstra's algorithm to update the time taken from the source node to all other nodes in a graph.

            Author: Ooi Yu Zhang

            Input:
                source_id: an integer representing the source node.
                carpool: a boolean value indicating whether the algorithm is allowed to go through edges that represent carpool lanes.

            Time complexity: O(|R|log|L|), where |L| is the total number of key locations and |R| is the total number of roads
            Aux space complexity: O(|L|+|R|), where |L| is the total number of key locations and |R| is the total number of roads

        '''
        # Initialising MinHeap
        min_heap = MinHeap(len(self.vertices))

        # Initialising the source node
        source = self.vertices[source_id]
        source.discovered = True
        source.visited = True
        source.time = 0

        # Reset all vertices for new instance of Dijkstra except source node
        for vertex in self.vertices:
            min_heap.append(vertex)
            if vertex.id != source_id:
                vertex.discovered = False
                vertex.visited = False
                vertex.time = inf

        # Traversing the Minheap
        while len(min_heap) > 0:
            # Popping the source node out
            curr_node = min_heap.serve()

            # Skip nodes that haven't been discovered
            if not curr_node.discovered:
                continue

            # Set current node as visited
            curr_node.visited = True

            # Check if current node is a node in the layered portion of the graph, if so, there is a passenger in the car
            if curr_node.id >= len(self.vertices) / 2:
                carpool = True
            else:
                carpool = False

            # Loop through all edges connected to current node
            for edge in curr_node.edges:
                # Initialise next_node as next node to check
                next_node = self.vertices[edge.b]

                # Initialise new time depending on whether in the carpool lane
                if carpool:
                    new_time = curr_node.time + edge.d
                else:
                    new_time = curr_node.time + edge.c

                # Check if next node has been discovered, if not, set it to be discovered and initialise time from current node to next node
                if not next_node.discovered:
                    next_node.discovered = True
                    next_node.time = new_time
                    next_node.previous = curr_node
                    min_heap.rise(next_node)

                # Check if next node has been visited, if not and the new time taken to reach next node is shorter, update time taken
                elif not next_node.visited and new_time < next_node.time:
                    next_node.time = new_time
                    next_node.previous = curr_node
                    min_heap.rise(next_node)

class MinHeap:
    """
    A class representing a priority queue implemented using heaps that prioritises minimum values
    Referenced MaxHeap from FIT1008 notes, modified to be a MinHeap and work with variables from this assignment
    """
    MIN_CAPACITY = 1

    def __init__(self, max_size: int) -> None:
        '''
        Constructor for MinHeap class
        '''
        self.length = 0
        self.heap_arr = [None] * (max(self.MIN_CAPACITY, max_size) + 1)
        self.index_arr = [None] * max(self.MIN_CAPACITY, max_size)

    def __len__(self) -> int:
        '''
        Returns the length of the heap
        '''
        return self.length

    def append(self, vertex) -> None:
        '''
        Appends a node onto the heap
        '''
        self.length += 1
        self.heap_arr[self.length] = vertex
        self.index_arr[vertex.id] = self.length
        self.rise(vertex)

    def swap(self, child_index: int, parent_index: int) -> None:
        '''
        Swaps two given nodes in both the heap array and the index array
        '''
        child, parent = self.heap_arr[child_index].id, self.heap_arr[parent_index].id
        self.index_arr[child], self.index_arr[parent] = parent_index, child_index
        self.heap_arr[child_index], self.heap_arr[parent_index] = self.heap_arr[parent_index], self.heap_arr[child_index]

    def serve(self):
        '''
        Retrieves the root of the heap
        '''
        self.swap(1, self.length)
        vertex = self.heap_arr.pop()
        self.length -= 1
        if self.length:
            self.sink(self.heap_arr[1])
        return vertex

    def rise(self, root) -> None:
        '''
        Rises a node to its correct position
        '''
        root_index = self.index_arr[root.id]
        while root_index > 1 and self.heap_arr[root_index].time < self.heap_arr[root_index // 2].time:
            self.swap(root_index, root_index // 2)
            root_index = root_index // 2

    def sink(self, root) -> None:
        '''
        Sinks a node to its correct position
        '''
        root_index = self.index_arr[root.id]
        while 2 * root_index <= self.length:
            child = self.smallest_child(root)
            if self.heap_arr[root_index].time <= self.heap_arr[child].time: #compare location time here, equals might be wrong check ltr
                break
            self.swap(child, root_index)
            root_index = child

    def smallest_child(self, root) -> None:
        '''
        Finds the smallest child of the given node
        '''
        root_index = self.index_arr[root.id]
        if 2 * root_index == self.length or self.heap_arr[2 * root_index].time < self.heap_arr[2 * root_index + 1].time: #compare location time here
            return 2 * root_index
        else:
            return 2 * root_index + 1

def optimalRoute(start, end, passengers, roads):
    '''
        Function description:
            This function returns the route with the shortest time needed from start to end which has been computed through the use of Dijkstra's algorithm.

        Approach description:
            The main concept used in implementing this function was using a single Dijkstra to traverse through a layered graph.
            As the graph can only ever have two versions, which are driving alone from start to end and driving alone from start to a location where
            a passenger is picked up and to the end, I have used the idea of creating two same layers in my graph, both layers connected through the nodes where
            there are passengers that can be picked up. To enable Dijkstra to traverse through the vertices, the IDs of the vertices in the second layer have been
            incremented so that Dijkstra's algorithm sees them as unique nodes, this effect is reversed in this optimalRoute function to give the correct route.
            This approach essentially allows Dijkstra to give the shortest route driving alone from start to finish as well as the shortest route after picking up
            a passenger all in the same graph. By giving each vertex a previous node as an attribute, this allows us to backtrack from the end node to the start node
            using the shortest time taken. Taking into account the possibility that driving alone from start to end may be faster than a route which involve picking
            up a passenger, this function compares the results of backtracking from the end node in the layered portion of the graph which involves picking up a passenger
            and backtracking from the end node in the original portion of the graph which involves driving alone, and gives us the shortest time.

        Author: Ooi Yu Zhang

        Precondition: The variable route contains the route with the shortest time needed from start to end.id.

        Postcondition: The variable route contains the route with the shortest time needed from start to end.id.

        Input:
            start: an integer indicating the departure location
            end: an integer indicating the destination location
            passengers: an array based list containing integers indicating locations with potential passengers
            roads: an array based list of tuples

        Output:
            route: An array based list of integers which represent the optimal route from the departure location to the destination location

        Time complexity: O(|R|log|L|), where |L| is the total number of key locations and |R| is the total number of roads
        Aux space complexity: O(|L|+|R|), where |L| is the total number of key locations and |R| is the total number of roads
    '''
    def backtracking(end, next_end):
        '''
        Recursive backtracking algorithm used to backtrack from the end node to the start node
        '''
        # If end node is None, return empty array
        if not end:
            return []
        # Check if end node is part of the layered graph, if so, compute the correct ID of the node accordingly
        if end.id >= len(graph.vertices) / 2:
            end.id = end.id - (len(graph.vertices) // 2)
        # Recursive step
        res = backtracking(end.previous, end.id)
        # Check if two consecutive nodes are the same, if so, this means there is a traversal in the graph to its layered portion
        if not next_end == end.id:
            res.append(end.id)
        return res

    # Create graph using the provided information
    graph = Graph(passengers, roads)

    # Using Dijkstra's algorithm to find shortest time from start to every location in the graph
    graph.dijkstra(start, False)

    # Check whether it is faster to go to destination alone or after picking up a passenger
    if graph.vertices[end].time < graph.vertices[end+(len(graph.vertices)//2)].time:
        route = backtracking(graph.vertices[end], None)
    else:
        route = backtracking(graph.vertices[end+(len(graph.vertices)//2)], None)

    return route

############################
######## Question 2 ########
############################

def select_sections(prob):
    '''
        Function description:
            This function returns a list containing the minimum total occupancy for the selected sections to be removed and a list of tuples in the form of (i, j)
            where each tuple represents the location of one section selected for removal. This function uses dynamic programming for efficiency.

        Approach descriptions:
            The main concept in implementing this function was the use of Dynamic Programming by creating a table to store all results computed so far
            and reusing those results instead of recomputing them to reduce time complexity. The approach used to solve the problem involves going from
            the top to the bottom of the input list. For every value in the input list, the function will check all values diagonal or vertical to it and
            obtain the minimum value amongst them. This value, along with the current value in the input list, will be added together and be stored in the
            memory in a similar position, not exactly the same as a list of 0s is used as the first list in the memory as the base case. This process
            repeats until the function reaches the last value in the last inner list in the input list. Finally, the minimum value from the last inner list
            as well as its location of sections is returned.

        Author: Ooi Yu Zhang

        Precondition: The variable min(memo[n]) contains the list with the minimum total occupancy and locations of sections for removal up to the n-th row.

        Postcondition: The variable min(memo[n]) contains the list with the minimum total occupancy and locations of sections for removal up to the n-th row.

        Input:
            prob: a list of lists where each list represents different rows of sections

        Output:
            A list containing the minimum total occupancy for the selected sections to be removed and a list of tuples in the form of (i, j)
            where each tuple represents the location of one section selected for removal

        Time complexity: O(nm) where n is the number of rows and m is the number of columns/aisles
        Aux space complexity: O(nm) where n is the number of rows and m is the number of columns/aisles
    '''
    # Memory for dynamic programing
    memo = [[[0, []] for i in range(len(prob[0]))] for i in range(len(prob) + 1)]
    # Looping through the memory and input list
    for n in range(1, len(prob) + 1):
        for m in range(len(prob[0])):
            # If at the end of an inner list, there are no values to the top right of value at current index
            if m == len(prob[0]) - 1:
                # Compute smaller total occupancy between values in memory above current total occupancy
                include = min(memo[n-1][m-1], memo[n-1][m])
            # If at the start of an inner list, there are no values to the top left of value at current index
            elif m == 0:
                # Compute smaller total occupancy between values in memory above current total occupancy
                include = min(memo[n-1][m], memo[n-1][m+1])
            else:
                # Compute smallest total occupancy between values in memory above current total occupancy
                include = min(memo[n-1][m-1], min(memo[n-1][m], memo[n-1][m+1]))

            # Update current total occupancy in memory with smallest total occupancy computed
            memo[n][m][0] = include[0] + prob[n-1][m]

            # Append location of sections from previous memory
            memo[n][m][1] += include[1]

            # Append location of sections belonging to the total occupancy computed to current list of location of sections
            memo[n][m][1].append((n-1, m))

    # Obtain minimum total occupancy from last row
    res = min(memo[-1])

    # Initialise minimum total occupancy
    minimum_total_occupancy = res[0]

    # Initialise location of sections for removal
    sections_location = res[1]

    return [minimum_total_occupancy, sections_location]


if __name__ == "__main__":
    #####################
    ### Provided Test ###
    #####################
    # Example for Question 1
    start = 0
    end = 4
    # The locations where there are potential passengers
    passengers = [2, 1]
    # The roads represented as a list of tuple
    roads = [(0, 3, 5, 3), (3, 4, 35, 15), (3, 2, 2, 2), (4, 0, 15, 10),
    (2, 4, 30, 25), (2, 0, 2, 2), (0, 1, 10, 10), (1, 4, 30, 20)]
    # Your function should return the optimal route (which takes 27 minutes).
    expected = [0, 3, 2, 0, 3, 4]
    #print(optimalRoute(start, end, passengers, roads) == expected)

    # Example for Question 2
    occupancy_probability = [
    [31, 54, 94, 34, 12],
    [26, 25, 24, 16, 87],
    [39, 74, 50, 13, 82],
    [42, 20, 81, 21, 52],
    [30, 43, 19, 5, 47],
    [37, 59, 70, 28, 15],
    [ 2, 16, 14, 57, 49],
    [22, 38, 9, 19, 99]]
    ss_selected = [118, [(0, 4), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 2), (7, 2)]]
    #print(select_sections(occupancy_probability) == ss_selected)

#########################################################################
######### Other tests provided by various students on Ed Forum ##########
#########################################################################

##############################
#### Tests For Question 1 ####
##############################

def test_different_shortest_paths():
        start = 2
        end = 5
        passengers = [3]
        roads = [
                (6, 2, 22, 6),
                (3, 6, 4, 3),
                (0, 7, 8, 3),
                (5, 0, 9, 6),
                (5, 4, 6, 5),
                (4, 3, 24, 2),
                (1, 2, 26, 23),
                (7, 4, 26, 8),
                (7, 3, 12, 5),
                (4, 5, 10, 3),
                (2, 0, 14, 1),
                (5, 7, 6, 6)
                ]
        res_1 = [2, 0, 7, 3, 6, 2, 0, 7, 4, 5] # Both results should yield 58 mins
        res_2 = [2, 0, 7, 4, 5]
        my_res = optimalRoute(start, end, passengers, roads)
        return my_res == res_1 or my_res == res_2

def test_start_at_some_location():
        start  = 6
        end = 7
        passengers = [4, 2, 9]
        roads = [
                (9, 0, 7, 4),
                (7, 4, 3, 1),
                (8, 7, 6, 1),
                (3, 5, 1, 1),
                (2, 9, 6, 4),
                (6, 4, 5, 4),
                (2, 4, 6, 2),
                (7, 3, 8, 7),
                (0, 9, 1, 1),
                (2, 3, 5, 5),
                (5, 3, 6, 6),
                (1, 9, 6, 5),
                (0, 7, 5, 5),
                (1, 8, 2, 1),
                (6, 9, 6, 5),
                (2, 1, 2, 2)
                ]
        result = [6, 9, 0, 7] # optimal route should take 15 mins
        return optimalRoute(start, end, passengers, roads) == result

def test_some_path_1():
        start = 0
        end = 5
        passengers = [2, 1]
        roads = [
                (4, 5, 200, 2),
                (0, 2, 2, 2),
                (1, 3, 10, 5),
                (3, 5, 50, 50),
                (2, 4, 10, 10),
                (0, 1, 1, 1)
                ]
        result = [0, 2, 4, 5]
        return optimalRoute(start, end, passengers, roads) == result

def test_reroute_from_start():
        start = 0
        end = 4
        passengers = [2, 1]
        roads = [
            (0,4,30,5),
            (0,1,5,4),
            (1,3,3,2),
            (3,2,2,1),
            (2,0,1,1)]
        result = [0, 1, 3, 2, 0, 4]
        return optimalRoute(start, end, passengers, roads) == result

def test_example():
        start = 0
        end = 4
        passengers = [2, 1]
        roads = [
            (0, 3, 5, 3),
            (3, 4, 35, 15),
            (3, 2, 2, 2),
            (4, 0, 15, 10),
            (2, 4, 30, 25),
            (2, 0, 2, 2),
            (0, 1, 10, 10),
            (1, 4, 30, 20),
        ]
        expected = [0, 3, 2, 0, 3, 4]
        return optimalRoute(start, end, passengers, roads) == expected
#######################################################################

#print(test_different_shortest_paths())
#print(test_start_at_some_location())
#print(test_some_path_1())
#print(test_reroute_from_start())
#print(test_example())

#######################################################################

##############################
#### Tests For Question 2 ####
##############################
def test_selectsections_7():
    occupancy_probability =  [
                [19, 76, 38, 22, 0],
                [56, 20, 54, 0, 34],
                [71, 86, 0, 99, 89],
                [81, 0, 82, 22, 45],
                [0, 22, 22, 93, 23]
                ]
    expected = [0, [(0, 4), (1, 3), (2, 2), (3, 1), (4, 0)]]
    my_res = select_sections(occupancy_probability)
    return my_res == expected

def test_selectsections_8():
    occupancy_probability =  [
                [19, 76, 38, 22, 0],
                [56, 20, 54, 0, 34],
                [71, 86, 0, 99, 89],
                [81, 34, 82, 0, 45],
                [62, 22, 22, 93, 0]
                ]
    expected = [0, [(0, 4), (1, 3), (2, 2), (3, 3), (4, 4)]]
    my_res = select_sections(occupancy_probability)
    return my_res == expected

def test_selectsections_6():
    occupancy_probability = [
                [19, 76, 38, 22],
                [56, 20, 54, 68],
                [71, 86, 15, 99],
                [81, 82, 82, 22],
                [36, 22, 22, 93]
                ]
    expected = [98, [(0, 0), (1, 1), (2, 2), (3, 3), (4, 2)]]
    my_res = select_sections(occupancy_probability)
    return my_res == expected

def test_selectsections_1():
    occupancy_probability = [[57, 11, 14, 19, 63, 50, 61, 50, 40,  0,  46],
                             [ 2, 42, 98, 84, 56,  5, 33, 87, 60, 19,  91],
                            [84, 23, 37, 36, 38, 89, 72, 13, 48, 88,  46],
                             [36, 91, 11,  1,  5,  3, 38, 58, 37, 24,  39],
                             [52, 74, 67, 41, 76, 29, 38, 61, 74, 42,  10],
                             [46, 25, 38, 16, 50,  7, 99, 34, 79, 83,  19],
                             [76, 68, 74, 48, 38, 11, 46, 25, 31, 10,  73],
                             [99,  4, 65, 22, 12, 47, 18, 45, 63, 85,  17],
                             [35, 86, 91, 69, 50, 20, 72, 34, 24, 69, 100],
                             [20,  7, 63, 92, 33, 81, 22, 79, 85, 39,  21],
                             [98, 22, 37, 54, 28, 89, 50, 95, 59, 17,  88],
                             [13, 86, 98, 26, 30,  3, 93, 97, 59,  1,  23],
                             [39, 62, 48, 37, 35, 84, 87, 91, 63, 66,  21]]
    expected = [273, [(0, 1), (1, 0), (2, 1), (3, 2), (4, 3), (5, 3), (6, 4), (7, 4), (8, 5), (9, 4), (10, 4), (11, 5), (12, 4)]]
    res = select_sections(occupancy_probability)
    return res == expected

def test_selectsections_2():
    occupancy_probability = [[15],[84],[82],[79],[77],[55],[69],[13],[21],[33],[85],[100],[67],[93],[3],[26],[29],[89],[36],[100],[68],[34],[87],[55],[47],[44],[64],[84],[41],[97]]
    expected = [1777, [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (16, 0), (17, 0), (18, 0), (19, 0), (20, 0), (21, 0), (22, 0), (23, 0), (24, 0), (25, 0), (26, 0), (27, 0), (28, 0), (29, 0)]]
    res = select_sections(occupancy_probability)
    return res == expected

def test_selectsections_3():
    occupancy_probability = [[66],[66]]
    expected = [132, [(0, 0), (1, 0)]]
    res = select_sections(occupancy_probability)
    return res == expected

def test_selectsections_4():
    occupancy_probability = [[32, 86, 95, 15, 68, 90],
                             [91, 88, 96, 51, 64, 66],
                             [17, 70, 13,  9, 90, 17],
                             [17, 15, 38, 12, 53, 17],
                             [29,  6, 18, 27, 66, 48],
                             [74, 43, 76, 44,  3,  1],
                             [89,  1,  8, 24, 45, 62],
                             [ 3, 98, 99, 89,  6, 66]]
    expected_1 = [147, [(0, 3), (1, 3), (2, 2), (3, 1), (4, 1), (5, 1), (6, 1), (7, 0)]]
    expected_2 = [147, [(0, 3), (1, 3), (2, 3), (3, 3), (4, 3), (5, 4), (6, 3), (7, 4)]]
    res = select_sections(occupancy_probability)
    return res == expected_1 or res == expected_2



#######################################################################

#print(test_selectsections_6())
#print(test_selectsections_7())
#print(test_selectsections_8())
#print(test_selectsections_1())
#print(test_selectsections_2())
#print(test_selectsections_3())
#print(test_selectsections_4())

#######################################################################

