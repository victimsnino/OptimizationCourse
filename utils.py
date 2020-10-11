import math

def fix_with_eps(value):
    eps = 0.00000001
    floor = math.floor(value)

    if value - floor <= eps:
        return floor
        
    ceil = math.ceil(value)
    if ceil - value <= eps:
        return ceil

    return value

def is_equal_with_eps(var1, var2):
    if fix_with_eps(var1) == fix_with_eps(var2):
        return True