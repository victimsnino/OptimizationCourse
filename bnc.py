
import time
from solver import *
import numpy as np

def maximal_independent_weighted_set(matrix, values):
    available_nodes = range(matrix.shape[0])
    find_neighbours = lambda x: set([j for j in available_nodes if matrix[x, j] == 1])

    node = int(argmax(values))
    neighbors = find_neighbours(node)
 
    indep_nodes = [node]
    not_neighbours = set(available_nodes).difference(neighbors.union(indep_nodes))
 
    while not_neighbours:
        list_not_neighbours = sorted(list(not_neighbours))
        modified_values = [v for i, v in enumerate(values) if i in list_not_neighbours]

        node = list_not_neighbours[argmax(modified_values)]
        indep_nodes.append(node)
 
        not_neighbours.difference_update(find_neighbours(node).union([node])) 
 
    return indep_nodes


class BnC:
    def __init__(self, input_matrix : np.array, timeout = 60*45):
        print("Start BNC")
        self.__timeout = timeout
        self.__time_start = time.time()
        self.__is_timeout = False

        self.__input_matrix = input_matrix
        self.__count = self.__input_matrix.shape[0]
        self.__degrees = np.array([ int(sum(self.__input_matrix[i, :])) for i in range(self.__count)])
        self.__solver = Solver(False)
        self.__solver.add_variables(self.__count)

        self.__best_solution_score = -1

        self.__add_initial_constraints()
        self.__branch_and_cut(True)
        print("")
    
    def result(self):
        return self.__best_solution_score, self.__is_timeout

    def __add_initial_constraints(self):
        for i in range(self.__count):
            self.__solver.add_constraint(maximal_independent_set(self.__input_matrix, i),  '<=', 1)

    def __separation(self, values):
        to_return = []
        for target in [values, values/self.__degrees]:
            res = maximal_independent_weighted_set(self.__input_matrix, target)
            total = sum([values[v] for v in res])
            if total > 1:
                to_return.append(res)
        return to_return
    
    def __check_solution(self, values):
        result = []
        for i in range(self.__count):
            if fix_with_eps(values[i]) != 1:
                continue
            for j in range(i+1, self.__count):
                if fix_with_eps(values[j]) != 1:
                    continue

                if self.__input_matrix[i,j] == 0:
                    result.append([i,j])
        return result

    def __branch_and_cut(self, first_level = False):
        if self.__is_timeout or time.time() - self.__time_start >= self.__timeout:
            print("Return by timeout")
            self.__is_timeout = True
            return
        
        prev_score = np.inf
        while(True):
            values = np.array(self.__solver.solve())
            score = sum_with_eps(values)

            #print(f'\x1b[1K\r[InProgress] Best score is {self.__best_solution_score} Current score is: {score}', end="")

            if math.floor(score) <= self.__best_solution_score:
                return
            
            diff = 0.001 if first_level else 0.01
            if (prev_score - score) < diff:
                break

            prev_score = score

            constraints = self.__separation(values)
            if len(constraints) == 0:
                break

            for constraint in constraints:
                self.__solver.add_constraint(constraint, '<=', 1)
        
        if is_integer_solution(values):
            constraints = self.__check_solution(values)
            if len(constraints) == 0:
                if score > self.__best_solution_score:
                    self.__best_solution_score = score
            else:
                for constraint in constraints:
                    self.__solver.add_constraint(constraint, '<=', 1)
                self.__branch_and_cut()
            return

        var_to_branch = get_variable_to_branch(values)
        for value in [1,0]:
            constr = self.__solver.add_constraint([var_to_branch], '==', value)
            self.__branch_and_cut()
            self.__solver.remove_constraint(constr)

