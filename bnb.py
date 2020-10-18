from numpy import argmax, argmin
from numpy.core.fromnumeric import var
from solver import Solver
from utils import *
import time

def is_integer_solution(values):
    return all([is_integer(val) for val in values])

def sum_with_eps(values):
    return sum([fix_with_eps(v) for v in values])

# maximal close to the 1
def get_variable_to_branch(values):
    return int(argmin([1 - fix_with_eps(v) if not is_integer(v) else 100 for v in values ]))

class BnB:
    def __init__(self, solver: Solver, min_value_of_heuristic = 0, timeout = 60*45):
        self.__solver = solver
        self.__min_value_of_heuristic = min_value_of_heuristic
        self.__timeout = timeout

        self.__best_known_solution = [0] # recursion

        self.__planar_history_constr_to_var = []

        self.__result = self.__solve_and_branching_planar()

    def result(self):
        return sorted([i for i, v in enumerate(self.__result) if fix_with_eps(v) == 1])

    def __planar_remove_constraints_if_need_for_new_variable(self, variable):
        '''
        Checks if we return to this node, but doesn't remove constraints
        '''
        found_index = -1
        for index, pack in enumerate(self.__planar_history_constr_to_var):
            if pack[1] == variable:
                found_index = index
                break

        if found_index == -1:
            return

        for i in range(len(self.__planar_history_constr_to_var)-1, found_index-1, -1):
            self.__solver.remove_constraint(self.__planar_history_constr_to_var[i][0])

        self.__planar_history_constr_to_var = self.__planar_history_constr_to_var[:found_index]

    def __planar_add_constraint(self, var, val):
        self.__planar_remove_constraints_if_need_for_new_variable(var)
        constr_id = self.__solver.add_constraint([var], '==', val)[0]
        self.__planar_history_constr_to_var.append([constr_id, var, val])

    def __planar_pop_constraint(self):
        self.__solver.pop_constraint()
        self.__planar_history_constr_to_var.pop()

    def __solve_and_branching_planar(self):
        time_start = time.time()

        best_int_solution = []
        best_int_solution_score = 0

        variables_to_branch = [[-1, -1]]
        while len(variables_to_branch) != 0:
            if time.time() - time_start >= self.__timeout:
                print("Return by timeout")
                return best_int_solution

            var_to_branch, value = variables_to_branch.pop()

            if var_to_branch != -1: # init
                self.__planar_add_constraint(var_to_branch, value)

            values = self.__solver.solve()
            score = sum_with_eps(values)
            if var_to_branch == -1: # first
                print(f"Init non-int score from cplex: {score}, heuristic init score: {self.__min_value_of_heuristic}")

            if score < self.__min_value_of_heuristic or \
               score < best_int_solution_score + 1: # +1 due to our best is 34, then all non-int solution < 35 is not suitable
                self.__planar_pop_constraint()
                continue

            if is_integer_solution(values):
                if score >= best_int_solution_score:
                    best_int_solution_score = score
                    best_int_solution = values
                    print(f"Found new solution:  {score}")
                    if var_to_branch == -1: # init
                        return best_int_solution
                        
                self.__planar_pop_constraint()
                continue
            
            variable_to_branch = get_variable_to_branch(values)

            variables_to_branch.append([variable_to_branch, 0])
            variables_to_branch.append([variable_to_branch, 1])

        return best_int_solution