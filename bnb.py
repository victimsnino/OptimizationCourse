from numpy import argmax, argmin
from solver import Solver
from utils import *

def is_integer_solution(values):
    return all([is_integer(val) for val in values])

def sum_with_eps(values):
    return sum([fix_with_eps(v) for v in values])

# maximal close to the 1
def get_variable_to_branch(values):
    return int(argmin([1 - fix_with_eps(v) if not is_integer(v) else 100 for v in values ]))

class BnB:
    def __init__(self, solver: Solver, min_value_of_heuristic = 0):
        self.__solver = solver
        self.__min_value_of_heuristic = min_value_of_heuristic
        self.__result = self.__solve_and_branching()

    def result(self):
        return sorted([i for i, v in enumerate(self.__result) if fix_with_eps(v) == 1])

    def __solve_and_branching(self):
        values = self.__solver.solve()
        if is_integer_solution(values):
            return values
        
        if sum_with_eps(values) < self.__min_value_of_heuristic:
            return values

        variable_to_branch = get_variable_to_branch(values)
        results = []
        # in this order due to i get variables with values close to 1
        for variable_value in [1, 0]:
           constraint_id = self.__solver.add_constraint([variable_to_branch], '==', 0)
           results.append(self.__solve_and_branching())
           self.__solver.remove_constraint(constraint_id)

        return results[int(argmax([sum_with_eps(v) if is_integer_solution(v) else 0 for v in results]))]