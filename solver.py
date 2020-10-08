import cplex
import itertools

def is_all_independent(matrix, indexes):
    for i,j in  itertools.combinations(indexes, 2):
        if matrix[i,j] == 1 or matrix[j,i] == 1:
            return False
    return True

class Solver:
    def __init__(self):
        self.__model = cplex.Cplex()
        self.__model.objective.set_sense(self.__model.objective.sense.maximize)

    def fill_from_matrix(self, matrix):
        size = matrix.shape[0]
        self.add_variables(size)

        for i,j in itertools.combinations(range(size), 2):
                if matrix[j, i] == 0 and i != j:
                    self.add_constraint([j, i], '<=', 1)

        return
        for i in range(size):
            indexes = [j for j in range(size) if matrix[i, j] == 0 and i != j]
            for length in range(2, min(4, len(indexes))):
                for combination in itertools.combinations(indexes, length):
                    target = [i]+list(combination)
                    if not is_all_independent(matrix, target):
                        continue

                    self.add_constraint(target, '<=', 1)

    def add_variables(self, count):
        self.__model.variables.add(obj=[1]*count,
                                   lb=[0]*count, 
                                   ub=[1]*count,
                                   types=[self.__model.variables.type.binary]*count)

    def add_constraint(self, indexes_or_variables, sense, value, multiples_for_indexes=None):
        valid_operations = ["<=", ">=", "=="]
        senses = ["L", "G", "E"]
        if sense not in valid_operations:
            raise Exception("Not valid operation! %s" % sense)

        if multiples_for_indexes is None:
            multiples_for_indexes = [1]*len(indexes_or_variables)
         
        target_sense = senses[valid_operations.index(sense)]
        self.__model.linear_constraints.add(lin_expr=[cplex.SparsePair(ind=indexes_or_variables,
                                                                       val=multiples_for_indexes)],
                                            senses=target_sense,
                                            rhs=[value])

    def solve(self):
        self.__model.set_results_stream(None)
        self.__model.write("example.lp")
        self.__model.solve()

        values = self.__model.solution.get_values()
        
        clique_points = [index for index, val in enumerate(values) if val > 0]
        return clique_points