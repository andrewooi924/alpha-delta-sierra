#################################
############ Imports ############
from math import inf
#################################
#################################

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

##############################
########### Tests ############
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
