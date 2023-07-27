#####################
###### Imports ######
#####################
from math import inf

class Edge:
    '''
    A basic class representing Edges in FlowNetwork
    '''
    def __init__(self, a, b, c) -> None:
        '''
        Constructor for the Edge class
        '''
        self.a = a
        self.b = b
        self.c = c

    def __str__(self) -> None:
        '''
        Return string for the Edge class
        '''
        res = "(" + str(self.a) + ", " + str(self.b) + ", " + str(self.c) + ")"
        return res

class Vertex:
    '''
    A basic class representing Vertices in FlowNetwork
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
        # Flow to previous Vertex
        self.flow = 0
        #Indicates whether this vertex is a target
        self.target = False

    def __str__(self) -> None:
        '''
        Return string for the Vertex class
        '''
        res = str(self.id) + " with edges ["
        i = 0
        while i < len(self.edges) - 1:
            res = res + str(self.edges[i]) + ", "
            i += 1
        if self.edges:
            res = res + str(self.edges[i])
        res = res + "]"
        return res

    def add_edge(self, edge) -> None:
        '''
        Adds an edge onto the vertex
        '''
        self.edges.append(edge)

class FlowNetwork:
    '''
    A basic class representing Flow Networks
    '''
    def __init__(self, edges, maxIn, maxOut, origin, targets) -> None:
        '''
        Constructor for the FlowNetwork class
        '''
        # Find total number of vertices in flow network
        self.vertices_count = -1
        for (a,b,c) in edges:
            self.vertices_count = max(self.vertices_count, max(a,b))

        # Initialise number of vertices in the flow network, with extra vertex as end node
        self.vertices = [None] * (2 * (self.vertices_count + 1) + 1)

        # Initialise vertices in the flow network
        for i in range(len(edges)):
            self.vertices[edges[i][0]] = Vertex(edges[i][0])
            self.vertices[edges[i][1]] = Vertex(edges[i][1])
            self.vertices[edges[i][0] + self.vertices_count + 1]  = Vertex(edges[i][0] + self.vertices_count + 1)
            self.vertices[edges[i][1] + self.vertices_count + 1]  = Vertex(edges[i][1] + self.vertices_count + 1)

        # Initialise target vertices as targets
        for i in targets:
            if self.vertices[i]:
                self.vertices[i].target = True
                self.vertices[i + self.vertices_count + 1].target = True

        # Initialise single sink
        self.vertices[len(self.vertices) - 1] = Vertex(len(self.vertices) - 1)

        # Initialise edges in the graph
        self.add_edges(edges, self.vertices_count, maxIn, maxOut)

        # Initialise origin
        self.origin = origin

    def __str__(self) -> None:
        '''
        Return string for Flow Networks
        '''
        res = ""
        for v in self.vertices:
            res = res + "Vertex " + str(v) + "\n"
        return res

    def add_edges(self, edges, vertices_count, maxIn, maxOut) -> None:
        '''
        Adds all given edges onto the flow network
        '''
        # Adding edges from connections using duplicated source vertices
        for i in range(len(edges)):
            u = edges[i][0]
            v = edges[i][1]
            w = edges[i][2]
            # Max capacity is minimum among channel, max incoming and max outgoing
            current_edge = Edge(u + self.vertices_count + 1, v, min(w, min(maxOut[u], maxIn[v])))
            current_vertex = self.vertices[u + self.vertices_count + 1]
            current_vertex.add_edge(current_edge)

        # Adding edges from vertices to their counterparts to emulate capacity inside of vertex
        for i in range(self.vertices_count + 1):
            # Adding edges for targets
            # If vertex is initialised
            if self.vertices[i]:
                # If vertex is a target
                if self.vertices[i].target:
                    # Adding edges from targets to their counterparts to emulate capacity inside of vertex
                    current_vertex = self.vertices[i]
                    current_edge = Edge(i, i + self.vertices_count + 1, maxIn[i])
                    current_vertex.add_edge(current_edge)

                    # Adding edges from targets to an end node for combined capacity
                    current_vertex = self.vertices[i + self.vertices_count + 1]
                    current_edge = Edge(i + self.vertices_count + 1, len(self.vertices) - 1, maxIn[i])
                    current_vertex.add_edge(current_edge)
                else:
                    # Adding edges from normal vertices to their counterparts
                    current_vertex = self.vertices[i]
                    current_edge = Edge(i, i + self.vertices_count + 1, maxOut[i])
                    current_vertex.add_edge(current_edge)

    def ford_fulkerson(self) -> int:
        '''
        Function description:
            This function utilises the Ford-Fulkerson algorithm to compute the maximum possible flow from an origin to a list of specified targets.

        Approach description:
            The main approach/concept in implementing this function was the use of duplicate vertices for each vertex to emulate the limits of
            incoming and outgoing flow each vertex can receive as vertices cannot have flow stored inside of them. As the minimum throughput is
            among the maximum throughput of an edge, and the maximum incoming and outgoing throughputs of a vertex, the minimum throughput is used
            as the value for connecting a vertex to its duplicate. An end node that all target nodes connect to is also used to compute combine all
            values to obtain the maximum throughput. The function continuously runs a BFS algorithm, which will run until there are no paths from
            the origin to the end node. Meanwhile, as long as the BFS is still running, the function will find the minimum throughput for every path
            and update the residual network accordingly, until there are no paths anymore, after which we will have a min cut in our flow network,
            giving us our maximum throughput.

        Author: Ooi Yu Zhang

        Output:
            flow: an integer representing the maximum possible data throughput from the data centre origin to the data centres specified in targets

        Time complexity: O(|D|*|C|^2) where D is the number of vertices (data centres) and C is the number of edges (communication channels)
        Aux space complexity: O(|D|+|C|) where D is the number of vertices (data centres) and C is the number of edges (communication channels)
        '''
        # Initialise max flow
        flow = 0

        # Initialise residual network
        residual_network = ResidualNetwork(self)

        # While there is an augmenting path in the residual network
        while residual_network.bfs(self.vertices[self.origin], self.vertices[-1]):

            # Take the augmenting path
            current = self.vertices[-1]
            path = []
            while current.id != self.origin:
                path.append(current.flow)
                current = self.vertices[current.previous.a]

            # Add the minimum from path to maximum possible throughput
            min_flow = min(path)
            flow += min_flow

            # Update residual network
            current = self.vertices[-1]
            while current.id != self.origin:
                edge = current.previous
                edge.c -= min_flow
                current = self.vertices[current.previous.a]

        return flow

class ResidualNetwork:
    '''
    A basic class representing Residual Networks
    '''
    def __init__(self, graph) -> None:
        '''
        Constructor for the ResidualNetwork class
        '''
        self.graph = graph

    def bfs(self, source, sink):
        '''
        Function for Breadth-First Search algorithm
        '''
        #Reset vertices
        for u in range(len(self.graph.vertices)):
            if self.graph.vertices[u]:
                self.graph.vertices[u].visited = False
                self.graph.vertices[u].discovered = False
                self.graph.vertices[u].previous = None

        res = []
        discovered = []
        discovered.append(source)
        while len(discovered) > 0:
            u = discovered.pop(0)

            # If reached the sink, return path
            if u.id == sink.id:
                return res

            u.visited = True
            res.append(u)
            for edge in u.edges:
                v = self.graph.vertices[edge.b]
                if v.discovered == False and edge.c:
                    discovered.append(v)
                    v.discovered = True
                    v.previous = edge
                    v.flow = edge.c

        return False

def maxThroughput(connections, maxIn, maxOut, origin, targets) -> int:
    '''
    Function description:
        This function utilises the Ford-Fulkerson algorithm to compute the maximum possible flow from an origin to a list of specified targets.

    Approach description:
        The main approach/concept in implementing this function was the use of duplicate vertices for each vertex to emulate the limits of
        incoming and outgoing flow each vertex can receive as vertices cannot have flow stored inside of them. As the minimum throughput is
        among the maximum throughput of an edge, and the maximum incoming and outgoing throughputs of a vertex, the minimum throughput is used
        as the value for connecting a vertex to its duplicate. An end node that all target nodes connect to is also used to compute combine all
        values to obtain the maximum throughput. The function continuously runs a BFS algorithm, which will run until there are no paths from
        the origin to the end node. Meanwhile, as long as the BFS is still running, the function will find the minimum throughput for every path
        and update the residual network accordingly, until there are no paths anymore, after which we will have a min cut in our flow network,
        giving us our maximum throughput.

    Author: Ooi Yu Zhang

    Input:
        connections: a list of tuples representing communication channels (edges)
        maxIn: list of integers where maxIn[i] specifies the maximum incoming flow that the data centre (vertex) can receive
        maxOut: list of integers where maxOut[i] specifies the maximum outgoing flow that the data centre (vertex) can send
        origin: an integer representing the starting vertex
        targets: a list of integers representing the data centres (vertices) to be reached
    Output:
        maxFlow: an integer representing the maximum possible data throughput from the data centre origin to the data centres specified in targets

    Time complexity: O(|D|*|C|^2) where D is the number of vertices (data centres) and C is the number of edges (communication channels)
    Aux space complexity: O(|D|+|C|) where D is the number of vertices (data centres) and C is the number of edges (communication channels)
    '''
    flownetwork = FlowNetwork(connections, maxIn, maxOut, origin, targets)
    maxFlow = flownetwork.ford_fulkerson()
    return maxFlow
