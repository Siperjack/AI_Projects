import copy
import itertools


class CSP:
    def __init__(self):
        # self.variables is a list of the variable names in the CSP
        self.variables = []

        # self.domains[i] is a list of legal values for variable i
        self.domains = {}

        # self.constraints[i][j] is a list of legal value pairs for
        # the variable pair (i, j)
        self.constraints = {}

        self.backtrack_calls = 0
        self.backtrack_fails = 0

    def add_variable(self, name, domain):
        """Add a new variable to the CSP. 'name' is the variable name
        and 'domain' is a list of the legal values for the variable.
        """
        self.variables.append(name)
        self.domains[name] = list(domain)
        self.constraints[name] = {}

    def get_all_possible_pairs(self, a, b):
        """Get a list of all possible pairs (as tuples) of the values in
        the lists 'a' and 'b', where the first component comes from list
        'a' and the second component comes from list 'b'.
        """
        return itertools.product(a, b)

    def get_all_arcs(self):
        """Get a list of all arcs/constraints that have been defined in
        the CSP. The arcs/constraints are represented as tuples (i, j),
        indicating a constraint between variable 'i' and 'j'.
        """
        return [(i, j) for i in self.constraints for j in self.constraints[i]]

    def get_all_neighboring_arcs(self, var):
        """Get a list of all arcs/constraints going to/from variable
        'var'. The arcs/constraints are represented as in get_all_arcs().
        """
        return [(i, var) for i in self.constraints[var]]

    def add_constraint_one_way(self, i, j, filter_function):
        """Add a new constraint between variables 'i' and 'j'. The legal
        values are specified by supplying a function 'filter_function',
        that returns True for legal value pairs and False for illegal
        value pairs. This function only adds the constraint one way,
        from i -> j. You must ensure that the function also gets called
        to add the constraint the other way, j -> i, as all constraints
        are supposed to be two-way connections!
        """
        if not j in self.constraints[i]:
            # First, get a list of all possible pairs of values between variables i and j
            self.constraints[i][j] = self.get_all_possible_pairs(self.domains[i], self.domains[j])

        # Next, filter this list of value pairs through the function
        # 'filter_function', so that only the legal value pairs remain
        self.constraints[i][j] = list(filter(lambda value_pair: filter_function(*value_pair), self.constraints[i][j]))

    def add_all_different_constraint(self, variables):
        """Add an Alldiff constraint between all of the variables in the
        list 'variables'.
        """
        for (i, j) in self.get_all_possible_pairs(variables, variables):
            if i != j:
                self.add_constraint_one_way(i, j, lambda x, y: x != y)

    def backtracking_search(self):
        """This functions starts the CSP solver and returns the found
        solution.
        """
        # Make a so-called "deep copy" of the dictionary containing the
        # domains of the CSP variables. The deep copy is required to
        # ensure that any changes made to 'assignment' does not have any
        # side effects elsewhere.
        assignment = copy.deepcopy(self.domains)

        # Run AC-3 on all constraints in the CSP, to weed out all of the
        # values that are not arc-consistent to begin with
        self.inference(assignment, self.get_all_arcs())

        # Call backtrack with the partial assignment 'assignment'
        return self.backtrack(assignment)

    def check_completion(self, assignment):
        #Check if assignment is complete
        complete = True
        #If any variable is undecided (>1), the assignment is not complete
        for var in assignment:
            if len(assignment[var]) != 1:
                complete = False
                break
        return complete


    def backtrack(self, assignment):
        self.backtrack_calls = self.backtrack_calls + 1
        """The function 'Backtrack' from the pseudocode in the
        textbook.

        The function is called recursively, with a partial assignment of
        values 'assignment'. 'assignment' is a dictionary that contains
        a list of all legal values for the variables that have *not* yet
        been decided, and a list of only a single value for the
        variables that *have* been decided.

        When all of the variables in 'assignment' have lists of length
        one, i.e. when all variables have been assigned a value, the
        function should return 'assignment'. Otherwise, the search
        should continue. When the function 'inference' is called to run
        the AC-3 algorithm, the lists of legal values in 'assignment'
        should get reduced as AC-3 discovers illegal values.

        IMPORTANT: For every iteration of the for-loop in the
        pseudocode, you need to make a deep copy of 'assignment' into a
        new variable before changing it. Every iteration of the for-loop
        should have a clean slate and not see any traces of the old
        assignments and inferences that took place in previous
        iterations of the loop.
        """
        #Checking completion using function defined above
        if self.check_completion(assignment):
            return assignment
        #For now, we select the variable closest to completion (shortest branch)
        var = self.select_unassigned_variable(assignment)

        for legal_value in assignment[var]:
            #Create deep copy to ensure recursive assignment edits have to effect on upper layers
            ass_copy = copy.deepcopy(assignment)
            ass_copy[var] = legal_value
            #Check consistency and call backtrack recursively
            if self.inference(ass_copy, self.get_all_neighboring_arcs(var)):
                result = self.backtrack(ass_copy)
                if result:
                    return result

        self.backtrack_fails = self.backtrack_fails +1
        return 

    """ NOT NECESSARRY - STUB FUNCTION
    def order_domain_values(self, var, assignment){
        #Least constraining value-sorting
        shortest = [None, 11111111]
        for domain, values in assignment.constraints[var]:

    }
    """
    
    def select_unassigned_variable(self, assignment):
        #Default move None with length larger than board
        #None can be easily identified if I wan't to bugtest
        best = [None, 11111111]
        #Find the variable with the lowest number of legal moves that are greater than 0
        #If there are several, we pick the first one.
        for var in assignment:
            if len(assignment[var]) > 1: #and len(assignment[var]) < best[1]:
                #Why the part that is commented out makes the algorithm way worse is beyond me.
                best = [var, len(assignment[var])]
        #For now we return only the variable
        return best[0]


    def inference(self, assignment, queue):
        """The function 'AC-3' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'queue'
        is the initial queue of arcs that should be visited.
        """
        while len(queue) > 0:
            #Remove from the front for queue properties:
            i,j = queue.pop(0)
            if self.revise(assignment, i, j):
                if len(assignment[i]) == 0:
                    return False
                #Neighbors is just a list
                neighbors = self.get_all_neighboring_arcs(i)
                #Queue comes from get_all_arcs, meaning it's all connections [i,j] found in constraints.
                for neighbor in neighbors:
                    if neighbor != (j,i) and neighbor != (i,j):
                        queue.append(neighbor)

        return True
    
    def revise(self, assignment, vari, varj):
        """The function 'Revise' from the pseudocode in the textbook.
        'assignment' is the current partial assignment, that contains
        the lists of legal values for each undecided variable. 'i' and
        'j' specifies the arc that should be visited. If a value is
        found in variable i's domain that doesn't satisfy the constraint
        between i and j, the value should be deleted from i's list of
        legal values in 'assignment'.
        """
        # TODO: IMPLEMENT THIS
        revised = False
        # print(f"key is: {vari}")
        # print(f"assignment[vari] is: \n {assignment[vari]}")
        for value1 in assignment[vari]:
            for value2 in assignment[varj]:
                if (value1,value2) not in self.constraints[vari][varj]:
                    assignment[vari].remove(value1)
                    revised = True
        return revised
    
def create_map_coloring_csp():
    """Instantiate a CSP representing the map coloring problem from the
    textbook. This can be useful for testing your CSP solver as you
    develop your code.
    """
    csp = CSP()
    states = ['WA', 'NT', 'Q', 'NSW', 'V', 'SA', 'T']
    edges = {'SA': ['WA', 'NT', 'Q', 'NSW', 'V'], 'NT': ['WA', 'Q'], 'NSW': ['Q', 'V']}
    colors = ['red', 'green', 'blue']
    for state in states:
        csp.add_variable(state, colors)
    for state, other_states in edges.items():
        for other_state in other_states:
            csp.add_constraint_one_way(state, other_state, lambda i, j: i != j)
            csp.add_constraint_one_way(other_state, state, lambda i, j: i != j)
    return csp


def create_sudoku_csp(filename):
    """Instantiate a CSP representing the Sudoku board found in the text
    file named 'filename' in the current directory.
    """
    csp = CSP()
    board = list(map(lambda x: x.strip(), open(filename, 'r')))

    for row in range(9):
        for col in range(9):
            if board[row][col] == '0':
                csp.add_variable('%d-%d' % (row, col), list(map(str, range(1, 10))))
            else:
                csp.add_variable('%d-%d' % (row, col), [board[row][col]])

    for row in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for col in range(9)])
    for col in range(9):
        csp.add_all_different_constraint(['%d-%d' % (row, col) for row in range(9)])
    for box_row in range(3):
        for box_col in range(3):
            cells = []
            for row in range(box_row * 3, (box_row + 1) * 3):
                for col in range(box_col * 3, (box_col + 1) * 3):
                    cells.append('%d-%d' % (row, col))
            csp.add_all_different_constraint(cells)

    return csp


def print_sudoku_solution(solution):
    """Convert the representation of a Sudoku solution as returned from
    the method CSP.backtracking_search(), into a human readable
    representation.
    """
    for row in range(9):
        for col in range(9):
            print(solution['%d-%d' % (row, col)][0], end=" "),
            if col == 2 or col == 5:
                print('|', end=" "),
        print("")
        if row == 2 or row == 5:
            print('------+-------+------')



#Solving using the implemented functions
sudoku_easy = create_sudoku_csp("easy.txt")
completed_sudoku_easy = sudoku_easy.backtracking_search()
if completed_sudoku_easy != None:
    print_sudoku_solution(completed_sudoku_easy)
    print("\nCalls: ", sudoku_easy.backtrack_calls, "\nFails: ", sudoku_easy.backtrack_fails)

sudoku_medium = create_sudoku_csp("medium.txt")
completed_sudoku_medium = sudoku_medium.backtracking_search()
if completed_sudoku_medium != None:
    print_sudoku_solution(completed_sudoku_medium)
    print("\nCalls: ", sudoku_medium.backtrack_calls, "\nFails: ", sudoku_medium.backtrack_fails)

sudoku_hard = create_sudoku_csp("hard.txt")
completed_sudoku_hard = sudoku_hard.backtracking_search()
if completed_sudoku_hard != None:
    print_sudoku_solution(completed_sudoku_hard)
    print("\nCalls: ", sudoku_hard.backtrack_calls, "\nFails: ", sudoku_hard.backtrack_fails)

sudoku_veryhard = create_sudoku_csp("veryhard.txt")
completed_sudoku_veryhard = sudoku_veryhard.backtracking_search()
if completed_sudoku_veryhard != None:
    print_sudoku_solution(completed_sudoku_veryhard)
    print("\nCalls: ", sudoku_veryhard.backtrack_calls, "\nFails: ", sudoku_veryhard.backtrack_fails)