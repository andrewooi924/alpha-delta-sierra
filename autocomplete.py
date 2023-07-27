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
