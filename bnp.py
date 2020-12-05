import datetime
from networkx.algorithms.structuralholes import constraint
from networkx.classes.function import neighbors
import numpy as np
import time

from numpy.core.fromnumeric import var
from solver import *
import networkx as nx
import operator
from bnc import maximal_independent_weighted_set_fast

class BnP:
    def __init__(self, input_matrix : np.array, timeout = 60*60):
        print(f"\n{datetime.datetime.now()}: Start BNC")
        self.__timeout = timeout
        self.__time_start = time.time()
        self.__is_timeout = False

        self.__input_matrix = input_matrix
        self.__count = self.__input_matrix.shape[0]

        self.__colors = self.__generate_initial_colors_and_constraints()
        self.__best_count_of_colors = 10000000000000
        self.__branch_colors_force_one = []
        self.__branch_colors_force_zero = []
        self.__solve()
        
    def result(self):
        return self.__best_count_of_colors, self.__is_timeout

    def __maximize_color(self, color_set):
        available_nodes = [n for n in range(self.__count) if n not in color_set]
        find_neighbours = lambda x: set([j for j in available_nodes if self.__input_matrix[x, j] == 1])

        for selected in color_set:
            neighbors = find_neighbours(selected)
            available_nodes = [n for n in available_nodes if n not in neighbors]

        result = color_set
        while available_nodes:
            selected = available_nodes.pop()
            result.append(selected)

            neighbors = find_neighbours(selected)
            available_nodes = [n for n in available_nodes if n not in neighbors]
        return result

    def __generate_initial_colors_and_constraints(self):
        G = nx.from_numpy_matrix(self.__input_matrix)
        result = []
        for strategy in ['largest_first', 'random_sequential', 'smallest_last', 'independent_set', 'connected_sequential_bfs', 'saturation_largest_first']:
            node_to_color = nx.algorithms.coloring.greedy_color(G, strategy=strategy)
            color_to_node = {}
            for node, color in node_to_color.items():
                color_to_node.setdefault(color, [])
                color_to_node[color].append(node)

            for color_set in color_to_node.values():
                color_set = sorted(self.__maximize_color(color_set))
                if color_set not in result:
                    result.append(color_set)
        
        return result

    def __build_exact_model(self, solution):
        exact_model = Solver(binary=True, max=True)
        for v in range(self.__count):
            exact_model.add_variables(1, obj=solution[v]+0.0001)

        for i in range(self.__count):
            for j in range(i+1, self.__count):
                if self.__input_matrix[i,j] == 1:
                    exact_model.add_constraint([i,j], '<=', 1)

        return exact_model.solve()

    def __column_generation(self, exact = False):
        exact = True
        model = Solver(binary=False, max=True)
        model.add_variables(self.__count)

        for i, c in enumerate(self.__colors):
            constraint = copy.deepcopy(c)
            multiples_for_variables = [1]*len(constraint)
            if i in self.__branch_colors_force_one:
                constraint.append(model.add_variables(1, obj=1)[0])
                multiples_for_variables.append(1)
            
            if i in self.__branch_colors_force_zero:
                constraint.append(model.add_variables(1, obj=0)[0])
                multiples_for_variables.append(-1)

            model.add_constraint(constraint, '<=', 1, multiples_for_variables)
        
        old_value = 100000
        while(True):
            solution = model.solve()

            if exact:
                new_color = sorted(self.__build_exact_model(solution))
            else:
                new_color = sorted(maximal_independent_weighted_set_fast(self.__input_matrix, solution[:self.__count]))

            if sum([solution[v] for v in new_color]) >  1:
                self.__colors.append(new_color)
                model.add_constraint(new_color, '<=', 1)
            else:
                break
            
            # tailing
            value = sum_with_eps(solution)
            if old_value - value < 0.001:
                break
            
            old_value = value

        return solution

    def __is_possible_prune(self, values):
        sum = sum_with_eps(values)
        return fix_with_eps(sum - (self.__best_count_of_colors - 1)) > 0

    def __solve(self):
        last_solution = self.__column_generation(exact=False)
        if self.__is_possible_prune(last_solution) or is_integer_solution(last_solution):
            last_solution = self.__column_generation(exact=True)

        # prune branch
        if self.__is_possible_prune(last_solution):
            return
        
        if is_integer_solution(last_solution):
            self.__best_count_of_colors = sum_with_eps(last_solution)
            return

        # branching
        var_to_branch = get_variable_to_branch(last_solution)
        
        self.__branch_colors_force_one.append(var_to_branch)
        self.__solve()
        self.__branch_colors_force_one.pop()

        self.__branch_colors_force_zero.append(var_to_branch)
        self.__solve()
        self.__branch_colors_force_zero.pop()