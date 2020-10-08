import cplex

class Solver:
    def __init__(self):
        self.__model = cplex.Cplex()
        self.__model.objective.set_sense(self.__model.objective.sense.maximize)

    def fill_from_matrix(self, matrix):
        size = matrix.shape[0]
        self.add_variables(size)

        for i in range(size):
            for j in range(size):
                if matrix[i, j] == 0 and i != j:
                    self.add_constraint([i, j], '<=', 1)

    def add_variables(self, count):
        self.__model.variables.add(obj=[1]*count,
                                   lb=[0]*count, 
                                   ub=[1]*count,
                                   types=[self.__model.variables.type.integer]*count)

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
        self.__model.solve()

        values = self.__model.solution.get_values()
        
        clique_points = [index for index, val in enumerate(values) if val == 1]
        return clique_points