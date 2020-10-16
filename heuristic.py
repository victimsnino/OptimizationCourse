import numpy as np
import operator


class HeuristicSearcher:
    def __init__(self, matrix : np.array):
        self.__result = self.__search(matrix)

    def result(self):
        return self.__result

    def __find_clique_for(self, node, degrees_sorted, matrix):
        clique = [degrees_sorted[node][0]]
        for i, _ in degrees_sorted:
            if all(matrix[i,j] == 1 for j in clique):
                clique.append(i)
        
        return len(clique)

    def __search(self, matrix):
        degrees = [ (i, int(sum(matrix[i, :]))) for i in range(matrix.shape[0])]
        degrees_sorted = sorted(degrees, key=operator.itemgetter(1), reverse=True)
        
        clique_sizes =[self.__find_clique_for(degrees_sorted[i][0], degrees_sorted, matrix) for i in range(30)]
        return max(clique_sizes)
            

