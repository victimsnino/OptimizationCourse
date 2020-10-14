from numpy import argmax, argmin
from numpy.core.fromnumeric import var
from solver import Solver
from utils import *

def is_integer_solution(values):
    return all([is_integer(val) for val in values])

def sum_with_eps(values):
    return sum([fix_with_eps(v) for v in values])

# maximal close to the 1
def get_variable_to_branch(values):
    return int(argmin([abs(0.5 - fix_with_eps(v)) if not is_integer(v) else 100 for v in values ]))

class BnB:
    def __init__(self, solver: Solver, min_value_of_heuristic = 0):
        self.__solver = solver
        self.__min_value_of_heuristic = min_value_of_heuristic

        self.__best_known_solution = [0] # recursion

        self.__planar_contraint_id_history = []
        self.__planar_branched_var_history = []

        self.__result = self.__solve_and_branching_planar()

    def result(self):
        return sorted([i for i, v in enumerate(self.__result) if fix_with_eps(v) == 1])

    def __planar_remove_constraints_if_need_for_new_variable(self, variable):
        '''
        Checks if we return to this node, but doesn't remove constraints
        '''
        if variable in self.__planar_branched_var_history:
            index = self.__planar_branched_var_history.index(variable)
            for v in range(len(self.__planar_branched_var_history)-1, index-1, -1):
                self.__solver.remove_constraint(self.__planar_contraint_id_history[v])

            self.__planar_branched_var_history = self.__planar_branched_var_history[:index]
            self.__planar_contraint_id_history = self.__planar_contraint_id_history[:index]

    def __planar_add_constraint(self, var, val):
        self.__planar_remove_constraints_if_need_for_new_variable(var)
        constr_id = self.__solver.add_constraint([var], '==', val)
        self.__planar_contraint_id_history.append(constr_id)
        self.__planar_branched_var_history.append(var)

    def __planar_pop_constraint(self):
        self.__solver.pop_constraint()
        self.__planar_contraint_id_history.pop()
        self.__planar_branched_var_history.pop()

    def __solve_and_branching_planar(self):
        best_int_solution = []
        best_int_solution_score = 0

        variables_to_branch = [[-1, -1]]
        solutions = []
        history_of_variables_to_branch = []
        while len(variables_to_branch) != 0:
            var_to_branch, value = variables_to_branch.pop()

            if var_to_branch != -1: # init
                self.__planar_add_constraint(var_to_branch, value)

            values = self.__solver.solve()
            score = sum_with_eps(values)
            if var_to_branch == -1: # first
                print(f"Best available score:{score}, heuristic best score:{self.__min_value_of_heuristic}")

            if score < self.__min_value_of_heuristic or score < best_int_solution_score + 1: # +1 due to our best is 34, then all non-int solution < 35 is not suitable
                self.__planar_pop_constraint()
                continue

            if values in solutions:
                self.__planar_pop_constraint()
                continue
            
            solutions.append(values)

            if is_integer_solution(values):
                if score >= best_int_solution_score:
                    best_int_solution_score = score
                    best_int_solution = values
                    print(score, variables_to_branch)
                    return best_int_solution

                self.__planar_pop_constraint()
                continue
            
            variable_to_branch = get_variable_to_branch(values)

            variables_to_branch.append([variable_to_branch, 0])
            variables_to_branch.append([variable_to_branch, 1])
            if sorted(variables_to_branch) in history_of_variables_to_branch:
                print("FIND!!!!")
            history_of_variables_to_branch.append(sorted(variables_to_branch))

        return best_int_solution

    def __solve_and_branching(self):
        values = self.__solver.solve()

        score = sum_with_eps(values)

        if is_integer_solution(values):
            if sum_with_eps(self.__best_known_solution) < score:
                self.__best_known_solution = values
            return values
        
        if sum_with_eps(self.__best_known_solution) > score or score < self.__min_value_of_heuristic:
            return [0]*len(values)

        variable_to_branch = get_variable_to_branch(values)
        results = []
        # in this order due to i get variables with values close to 1
        for variable_value in [1, 0]:
           constraint_id = self.__solver.add_constraint([variable_to_branch], '==', variable_value)
           results.append(self.__solve_and_branching())
           self.__solver.remove_constraint(constraint_id)

        is_int = [is_integer_solution(v) for v in results]
        if sum(is_int) == 0:
            return [0]*len(results[0])
        if sum(is_int) == 2:
            return results[int(argmax([sum_with_eps(v) for v in results]))]
        return results[int(argmax(is_int))]