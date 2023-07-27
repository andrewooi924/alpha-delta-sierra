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

##############################
########### Tests ############
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
