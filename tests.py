import pytest
import os
from common import check_model_for
from solver import Solver
import numpy as np

def test_simple_clique():
    solver = Solver()
    matrix = np.zeros((6,6))
    edges = [[0,1], [0,2], [1,2], [3,0],[4,1], [5,2]]
    for i,j in edges:
        matrix[i,j] = 1
        matrix[j,i] = 1

    solver.fill_from_matrix(matrix)

    assert solver.solve() == [0, 1, 2]


@pytest.mark.parametrize("file_name", ["brock200_2"]) #"C125.9", "keller4", "brock200_2", "p_hat300-1"])
def test_for_real_data(file_name):
    full_name = os.path.abspath('.')+'\\samples\\'+file_name
    assert check_model_for(full_name+'.clq', full_name+'.txt', True) == True
