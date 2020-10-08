import numpy as np
from solver import Solver

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

def to_set_of_str_inc_1(indexes):
    return set([str(v+1) for v in indexes])

def check_model_for(input_path, answers_path, solve_while_found_solution = True):
    input_matrix = parse_input(input_path)
    answers = set(parse_answers(answers_path))

    solver = Solver()
    solver.fill_from_matrix(input_matrix)

    while(True):
        clique_points = to_set_of_str_inc_1(solver.solve())
        print(len(clique_points), len(answers))
        print(clique_points, answers)
        if clique_points == answers:
            return True
            
        if len(clique_points) != len(answers):
            return False

        if not solve_while_found_solution:
            return True

        for node_to_ban in clique_points.difference(answers):
            solver.add_constraint([int(node_to_ban)-1], '==', 0)
   