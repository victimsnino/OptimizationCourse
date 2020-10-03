import cplex

class Solver:
    def __init__(self):
        self.__model = cplex.Cplex()
        self.__model.objective.set_sense(self.__model.objective.sense.maximize)
        
    def add_variable(self, name, obj=1):
        if (name in self.__model.variables.get_names()):
            return

        self.__model.variables.add(obj=[obj],
                                 lb=[0], ub=[1],
                                 types=[self.__model.variables.type.binary],
                                 names=[name])

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
        self.__model.solve()

        status = self.__model.solution.get_status()
        text_stats = self.__model.solution.status[status]
        print(f"Solution status = {status} : {text_stats}")

        names = self.__model.variables.get_names()
        values = self.__model.solution.get_values()
        
        clique_points = [names[index] for index, val in enumerate(values) if val == 1]
        print(f"Clique points: {clique_points}")
        return values, clique_points