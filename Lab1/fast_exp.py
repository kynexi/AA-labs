def multiply_matrices(m1, m2):
    a1, b1, c1, d1 = m1
    a2, b2, c2, d2 = m2
    
    new_a = a1 * a2 + b1 * c2
    new_b = a1 * b2 + b1 * d2
    new_c = c1 * a2 + d1 * c2
    new_d = c1 * b2 + d1 * d2
    
    return (new_a, new_b, new_c, new_d)


def fibonacci(n):
    if n == 0:
        return 0
    if n == 1:
        return 1
    
    step = (1, 1, 1, 0)
    
    result = (1, 1, 1, 0)
    n = n - 1  
    
    while n > 0:
        if n & 1:
            result = multiply_matrices(result, step)
        step = multiply_matrices(step, step)
        
        n = n >> 1 # move to next bit
    
    return result[1]
