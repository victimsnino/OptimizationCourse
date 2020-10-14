import pytest
import os
from common import *
from solver import Solver
import numpy as np
import time
from utils import *
from bnb import BnB

def test_eps():
    assert is_equal_with_eps(0.1, 0.1)
    assert is_equal_with_eps(0.00000000000001, 0)
    assert is_equal_with_eps(-0.00000000000001, 0)
    assert is_equal_with_eps(1.00000000000001, 1)
    assert is_equal_with_eps(0.99999999999999, 1)
    assert is_equal_with_eps(0.9999, 0.9999)
    assert is_equal_with_eps(1.111111, 1.111111)
    assert is_equal_with_eps(1.000000000000001, 1)
    assert is_integer(0.0000000000000001)
    assert not is_integer(0.999)

def test_simple_clique():
    solver = Solver()
    matrix = np.zeros((7,7))
    edges = [[0,1], [0,2], [1,2], [3,0],[4,1], [5,2], [6,0],[6,1],[6,2], [6,3], [6,4]]
    for i,j in edges:
        matrix[i,j] = 1
        matrix[j,i] = 1

    solver.fill_from_matrix(matrix)

    assert solver.solve() == [0, 1, 2, 6]

def test_simple_bnb():
    solver = Solver(False, False)
    solver.add_variables(10)
    solver.add_constraint([0], '<=', 0.99)
    solver.add_constraint([1], '<=', 0.99)

    bnb = BnB(solver)
    assert bnb.result() == list(range(2,10))

@pytest.mark.parametrize("file_name", ["C125.9", "keller4", "brock200_2", "p_hat300-1"])
def test_for_real_data(file_name):
    full_name = os.path.abspath('.')+'\\samples\\'+file_name
    start = time.time()
    assert check_cplex_int_model_with_answers(full_name+'.clq', full_name+'.txt', False) == True
    end = time.time()
    print(f"Elapsed time: {end-start}")

@pytest.mark.parametrize("file_name",["C125.9", "keller4", "brock200_2", "p_hat300-1"])
def test_bnb(file_name):
    full_name = os.path.abspath('.')+'\\samples\\'+file_name
    start = time.time()

    assert check_model_with_custom_bnb(full_name+'.clq', full_name+'.txt')
   
    end = time.time()
    print(f"Elapsed time: {end-start}")
