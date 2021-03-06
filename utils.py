import math
from numpy import argmax, argmin, round

def fix_with_eps(value):
    eps = 0.0000000001
    floor = int(value)

    if value - floor <= eps:
        return floor

    ceil = floor + 1
    if ceil - value <= eps:
        return ceil

    return value

def is_integer(value):
    fixed = fix_with_eps(value)
    return round(fixed) == fixed

def is_equal_with_eps(var1, var2):
    if fix_with_eps(var1) == fix_with_eps(var2):
        return True

def is_integer_solution(values):
    for val in values:
        if not is_integer(val):
            return False

    return True

def sum_with_eps(values):
    return fix_with_eps(sum([fix_with_eps(v) for v in values]))

# maximal close to the 1
def get_variable_to_branch(values):
    return int(argmin([1 - fix_with_eps(v) if not is_integer(v) else 100000 for v in values ]))
