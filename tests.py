import pytest
import os
from common import check_model_for
from solver_with_vizualization  import SolveAndVizualize

def test_simple_clique():
    t = SolveAndVizualize(False)
    t.add_edge(1, 2)
    t.add_edge(1, 3)
    t.add_edge(2, 3)

    t.add_edge(4, 1)
    t.add_edge(5, 2)
    t.add_edge(6, 3)

    t.add_post_constrains_to_graph()
    assert t.solve() == ['1','2', '3']

def test_simple_clique_with_extend():
    t = SolveAndVizualize(False)
    t.add_edge(1, 2)
    t.add_edge(1, 3)
    t.add_edge(2, 3)

    t.add_edge(4, 1)
    t.add_edge(5, 2)
    t.add_edge(6, 3)

    t.add_edge(6, 8)
    t.add_edge(6, 9)

    t.add_edge(5, 10)
    t.add_edge(5, 11)

    t.add_post_constrains_to_graph()
    assert t.solve() == ['1','2', '3']

@pytest.mark.parametrize("file_name", ["C125.9", "keller4", "brock200_2", "p_hat300-1"])
def test_for_real_data(file_name):
    full_name = os.path.abspath('.')+'\\samples\\'+file_name
    assert check_model_for(full_name+'.clq',full_name+'.txt') == True