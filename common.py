from solver_with_vizualization  import SolveAndVizualize

def parse_input_to_solver(file_path):
    with open(file_path, 'r') as file:
        solver = SolveAndVizualize(False)
        for line in file:
            if not line.startswith('e '):
                continue
            splitted = line.rstrip().split(' ')
            solver.add_edge(splitted[1], splitted[2])

        solver.add_post_constrains_to_graph()
        return solver

def parse_answers(file_path):
    with open(file_path, 'r') as file:
        line = file.readline()
        return line.rstrip().split(' ')

def check_model_for(input_path, answers_path):
    solver = parse_input_to_solver(input_path)
    answers = parse_answers(answers_path)
    
    while(True):
        clique_points = solver.solve()
        if set(clique_points) == set(answers):
            return True
            
        if len(clique_points) != len(answers):
            return False

        for node_to_ban in set(clique_points).difference(answers):
            solver.ban_node(node_to_ban)
   