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

        self.__colors, self.__direct_model = self.__generate_initial_colors_and_model()
        self.__dual_model, self.__dual_variable_for_zero, self.__dual_variable_for_one = self.__generate_dual_model()
        self.__best_count_of_colors = 10000000000000
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

    def __generate_initial_colors_and_model(self):
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

        model = Solver(binary=False, max=False)
        model.add_variables(len(result))
        for node_i in range(self.__count):
            model.add_constraint([i for i, color in enumerate(result) if node_i in color], '>=', 1)

        return result, model

    def __generate_dual_model(self):
        model = Solver(binary=False, max=True)

        zero_variable = model.add_variables(1, ub=1, obj=0)[0]
        one_variable = model.add_variables(1, ub=1, obj=1)[0]

        model.add_variables(self.__count)

        for i, constraint in enumerate(self.__colors):
            model.add_constraint([v+2 for v in constraint], '<=', 1)

        return model,zero_variable, one_variable

    def __build_exact_model(self, solution):
        exact_model = Solver(binary=True, max=True)
        for v in range(self.__count):
            exact_model.add_variables(1, obj=solution[v]+0.0000000001)

        for i in range(self.__count):
            for j in range(i+1, self.__count):
                if self.__input_matrix[i,j] == 1:
                    exact_model.add_constraint([i,j], '<=', 1)

        slave_solution = exact_model.solve(True)
        print(f'Bound old {np.sum(solution)} new {np.sum(slave_solution)} result {np.sum(solution)/np.sum(slave_solution)}')
        print(slave_solution)
        return exact_model.solve(False)

    def __add_new_color(self, color):
        self.__colors.append(color)
        index_of_color = self.__direct_model.add_variables(1)[0]
        for c in color:
            self.__direct_model.set_coefficent_for_constraint(c, index_of_color, 1)

    def __column_generation(self, exact = False):
        old_value = 100000
        added_new_color = False
        while(True):
            solution = self.__dual_model.solve()[2:self.__count+2]
            if exact:
                new_color = sorted(self.__build_exact_model(solution))
            else:
                new_color = sorted(maximal_independent_weighted_set_fast(self.__input_matrix, solution))

            if sum([solution[v] for v in new_color]) <=  1:
                break
            
            self.__add_new_color(new_color)
            self.__dual_model.add_constraint([v+2 for v in new_color], '<=', 1)
            added_new_color = True
        
            # tailing
            value = sum_with_eps(solution)
            if old_value - value < 0.001:
                break
            
            old_value = value
        return added_new_color

    def __is_possible_prune(self, values):
        sum = sum_with_eps(values)
        return fix_with_eps(sum - (self.__best_count_of_colors - 1)) >= 0

    def __solve(self):
        self.__column_generation(exact=False)
        last_solution = self.__direct_model.solve()

        if self.__is_possible_prune(last_solution) or is_integer_solution(last_solution):
           self.__column_generation(exact=True)

        # last_solution = self.__direct_model.solve()
        print(f'\x1b[1K\rAfter if {sum_with_eps(last_solution)}', end="")

        # prune branch
        if self.__is_possible_prune(last_solution):
            return
        
        if is_integer_solution(last_solution):
            self.__best_count_of_colors = sum_with_eps(last_solution)
            print(f'New solution {self.__best_count_of_colors}')
            return

        # branching
        var_to_branch = get_variable_to_branch(last_solution)

        constr = self.__direct_model.add_constraint([var_to_branch], '>=', 1)
        self.__dual_model.set_coefficent_for_constraint(var_to_branch, self.__dual_variable_for_one, 1)
        self.__solve()
        self.__direct_model.remove_constraint(constr)
        self.__dual_model.set_coefficent_for_constraint(var_to_branch, self.__dual_variable_for_one, 0)

        if self.__is_possible_prune(last_solution):
            return
            
        constr = self.__direct_model.add_constraint([var_to_branch], '<=', 0)
        self.__dual_model.set_coefficent_for_constraint(var_to_branch, self.__dual_variable_for_zero, -1)
        self.__solve()
        self.__direct_model.remove_constraint(constr)
        self.__dual_model.set_coefficent_for_constraint(var_to_branch, self.__dual_variable_for_zero, 0)