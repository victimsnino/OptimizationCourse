from heuristic import HeuristicSearcher
import numpy as np
from solver import Solver
from utils import *
from bnb import BnB

def parse_input(file_path):
    with open(file_path, 'r') as file:
        out = None
        for line in file:
            if not line.startswith('e '):
                if line.startswith('p '):
                    size = int([r for r in line.rstrip().split(' ') if len(r) > 0][2])
                    out = np.zeros((size, size))
                continue

            if out is None:
                raise Exception("None")

            splitted = line.rstrip().split(' ')
            i = int(splitted[1]) - 1 
            j = int(splitted[2]) - 1
            out[i,j] = 1
            out[j,i] = 1

        return out

def parse_answers(file_path):
    with open(file_path, 'r') as file:
        line = file.readline()
        return line.rstrip().split(' ')

def to_set_of_indexes(indexes):
    return set([int(v)-1 for v in indexes])

def is_clique(indexes_set, matrix):
    indexes = list(indexes_set)
    for num_i, i in enumerate(indexes):
        for j in indexes[num_i+1:]:
            if matrix[i, j] == 0:
                return False
    return True

def check_cplex_int_model_with_answers(input_path, answers_path, solve_while_found_solution = True):
    input_matrix = parse_input(input_path)
    answers = to_set_of_indexes(parse_answers(answers_path))

    solver = Solver()
    solver.fill_from_matrix(input_matrix)

    while(True):
        clique_points = set(solver.solve())
        if clique_points == answers:
            return True

        if not is_clique(clique_points, input_matrix):
            return False
            
        if len(clique_points) != len(answers):
            return False

        if not solve_while_found_solution:
            return True

        for node_to_ban in clique_points.difference(answers):
            solver.add_constraint([node_to_ban], '==', 0)

def check_model_with_custom_bnb(input_path):
    input_matrix = parse_input(input_path)

    solver = Solver(binary=False)
    solver.fill_from_matrix(input_matrix)
    
    heuristic_size = HeuristicSearcher(input_matrix).result()
    
    bnb = BnB(solver, heuristic_size)
    res = bnb.result()
    print(f"Best solution results {len(res)}")
    return len(res)