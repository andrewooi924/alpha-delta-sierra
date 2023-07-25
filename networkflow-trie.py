'''''''''''''''''''''
Algorithms and Data Structures Assignment 2
Name: Ooi Yu Zhang
'''''''''''''''''''''

#####################
###### Imports ######
#####################
from math import inf

####################
###  Question 1  ###
####################

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

##################
### Question 2 ###
##################

class Node:
    '''
    A basic class representing Nodes

    Author: Ooi Yu Zhang
    '''
    def __init__(self, count=None, size=27) -> None:
        '''
        Constructor for Node class

        Input:
            count: an integer representing the word with the highest frequency that involves the letter stored in this node, else None
            size: an integer representing lowercase alphabets and a terminal, which by default is 27
        '''
        # Highest frequency of word involving letter in this node
        self.count = count
        # Letter represented by this node
        self.char = None
        # Next node for word with highest frequency or in lexicographic order otherwise
        self.next = None
        # Index of current letter represented with numbers from 1 to 26
        self.index = inf
        # List of links from this node to every alphabetical letter and the terminal
        self.links = [None] * size

class CatsTrie:
    '''
    A class representing CatsTrie, a Trie for the cat language

    Author: Ooi Yu Zhang
    '''
    def __init__(self, sentences) -> None:
        '''
        Function description:
            This function is a constructor for the CatsTrie class which initialises the Trie.

        Approach description:
            The main approach for initialising the CatsTrie is by recursively inserting each word from sentences into the CatsTrie
            by initialising each letter of the sentence as a Node and storing the details of the letter and the sentence for autocomplete
            inside the Node both during initialisation and during recursion. The details for both are discussed in the functions
            insert and insert_aux below.

        Author: Ooi Yu Zhang

        Input:
            sentences: a list of strings

        Time complexity: O(NM) where N is the number of sentences in the list sentences and M is the number of characters in the longest sentence
        Aux space complexity: O(NM) where N is the number of sentences in the list sentences and M is the number of characters in the longest sentence
        '''
        # Initialising the root node
        self.root = Node(count=0)
        # Level of root node is 0
        self.level = 0
        # Minimum level (in the case where frequency is the same, so we look at lexicographic order)
        self.minlevel = inf
        # Iterating through every word in the list, sentences
        for key in sentences:
            self.insert(key)

    def insert(self, key) -> None:
        '''
        Function description:
            This function inserts a sentence from the list, sentences into the CatsTrie

        Approach description:
            As this function is executed in a loop, the main approach is to always start from the root node, then recursively insert
            the sentence into the CatsTrie, character by character using the function insert_aux which is discussed below. After insertion,
            the details for the sentence to be used for autocomplete during an empty string is updated accordingly.

        Author: Ooi Yu Zhang

        Input:
            key: a string representing the current sentence to be inserted

        Time complexity: O(M) where M is the number of characters in the longest sentence
        Aux space complexity: O(M) where M is the number of characters in the longest sentence
        '''
        # Start from root node for every sentence
        current = self.root
        # Recursively insert sentence into CatsTrie
        res = self.insert_aux(current, key)
        # Update details at root node
        # If frequency of the newly inserted / existing sentence is greater than the current highest
        if res.count > current.count:
            # Update highest frequency
            current.count = res.count
            # Update autocomplete for empty string
            current.next = res
            # Update level for autocomplete
            self.minlevel = self.level
        # If same frequency but sentence is lexicographically smaller
        elif res.count == current.count and self.level < self.minlevel:
            # Update highest frequency
            current.count = res.count
            # Update autocomplete for empty string
            current.next = res
            # Update level for autocomplete
            self.minlevel = self.level

        # Reset counter for level
        self.level = 0

    def insert_aux(self, current, key):
        '''
        Function description:
            This function inserts each letter from the sentence to be inserted into the Trie recursively.

        Approach description:
            The main approach used in the implementation of this function is use of recursion where various information is
            passed into the current Node during initial insertion and during return of recursion. Firstly, a base case is
            established so the recursive calls will return when the function reaches the end of the sentence. Otherwise,
            if the base case is not reached, the function will try to move to the next letter in the sentence, if the letter
            doesn't exist, the function will initialise the letter as a new Node while updating all the related details.
            Once that is done, the recursive call is executed. On return of the recursive call, as we have already reached the
            end of the sentence, we know whether the newly added or existing sentence has a higher frequency than the current highest,
            hence we can check and update the autocomplete for every Node containing the letter in the sentence.

        Author: Ooi Yu Zhang

        Input:
            current: a Node representing the current character of the sentence to be inserted
            key: a string representing the current sentence to be inserted

        Output:
            current: a Node representing the current character of the sentence to be inserted

        Time complexity: O(M) where M is the number of characters in the longest sentence
        Aux space complexity: O(M) where M is the number of characters in the longest sentence
        '''
        # Base case, when at the end of current sentence
        if len(key) == 0:
            # If sentence already initialised previously (has a terminal)
            if current.links[0]:
                # Increment frequency
                current.links[0].count += 1
            # Sentence hasn't been previously initialised
            else:
                # Initialise terminal for new sentence
                current.links[0] = Node(count=1)
            # Return terminal
            return current.links[0]
        else:
            # Compute index for current letter using math (ASCII code - 97 + 1)
            index = ord(key[0]) - 97 + 1
            # If path exists
            if current.links[index]:
                # Move to next node
                current = current.links[index]
                # Increment counter for level
                self.level += 1
            # If path doesn't exist
            else:
                # Initialise new Node for letter
                current.links[index] = Node(count=0)
                # Initialise letter for Node
                current.links[index].char = key[0]
                # Move to next node
                current = current.links[index]
                # Initialise index of letter for Node
                current.index = index
                # Increment counter for level
                self.level += 1

            # Recursive call for insertion
            res = self.insert_aux(current, key[1:])

            # Update details for autocomplete word at current Node
            # If current sentence has higher frequency than current highest
            if res.count > current.count:
                # Update highest frequency
                current.count = res.count
                # Update path
                current.next = res
            # If current sentence has same frequency but lexicographically smaller
            elif res.index < current.next.index and res.count == current.count and current.next.index != inf:
                # Update path
                current.next = res
            # If current sentence has same frequency and the sentence is the prefix
            elif res.index == inf and res.count == current.count:
                # Update path
                current.next = res

            # Update on return during recursion
            return current

    def autoComplete(self, prompt):
        '''
        Function description:
            This function returns a string that represents the autocompleted sentence from the prompt

        Approach description:
            The main approach for this function is to first fully iterate through the prompt and check if the prompt itself
            is the sentence with the highest frequency or the lexicographically smallest sentence otherwise. If not, the function
            traverses through CatsTrie following the stored next Nodes in each of the Nodes leading up to the full autocompleted
            sentence. This works as we previously stored the sentence with the highest frequency or the lexicographically smallest
            in every Node, hence when reaching the end of the prompt, we function already knows which Node to traverse to next,
            and as a result the function already knows what the autocompleted sentence is and is retrieving it.

        Author: Ooi Yu Zhang

        Input:
            prompt: a string with the characters in the set of [a...z] representing the incomplete sentence that is to be completed by the CatsTrie

        Output:
            res: a string representing the autocompleted sentence from the given prompt, else None

        Time complexity:
            O(X+Y) where X is the length of the prompt and Y is the length of the most frequent sentence in sentences that begins with prompt
            O(X) if such a sentence does not exist where X is the length of the prompt
        Aux space complexity: O(1)
        '''
        # Begin from root
        current = self.root

        # Result (Autocomplete sentence)
        res = ""
        level = 0

        # Iterate through each character in prompt
        for char in prompt:
            # Compute index for current letter using math (ASCII code - 97 + 1)
            index = ord(char) - 97 + 1
            # If path exists
            if current.links[index]:
                # Move to next character
                current = current.links[index]
                # Increment counter for current level
                level += 1
                # Update autocomplete sentence
                res += current.char
            # If path does not exist
            else:
                # Prompt does not exist
                return None

        # If prompt is the sentence
        if not current.next and current.links[0]:
            return prompt
        elif current.next:
            # Write a loop that returns lexicographically the highest frequency autocomplete word from sentences
            while current.next.char:
                # Break if same frequency, lexicographically smaller
                if self.level == self.minlevel and current.links[0] and current.count == self.root.count:
                    break
                # Move to next character in sentence
                current = current.next
                # Update autocomplete sentence
                res += current.char
                # Increment counter for current level
                level += 1
            return res
        else:
            return None
