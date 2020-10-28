import math
from numpy import argmax, argmin

def fix_with_eps(value):
    eps = 0.0000000001
    floor = math.floor(value)

    if value - floor <= eps:
        return floor
        
    ceil = math.ceil(value)
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
    return all([is_integer(val) for val in values])

def sum_with_eps(values):
    return sum([fix_with_eps(v) for v in values])

# maximal close to the 1
def get_variable_to_branch(values):
    return int(argmin([1 - fix_with_eps(v) if not is_integer(v) else 100 for v in values ]))
