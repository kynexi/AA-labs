import time
from dp import fib as fib_dp
from recursion import fib as fib_recursion
from binet import fib as fib_binet
from simple_matrix import fib as fib_matrix
from fast_exp import fibonacci as fib_fast_exp


def test_function(func, n):
    start_time = time.time()
    result = func(n)
    end_time = time.time()
    
    elapsed = end_time - start_time
    return elapsed


test_values = [10, 20, 30, 40, 50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]

implementations = [
    #("Recursion", fib_recursion),
    ("DP", fib_dp),
    ("Binet", fib_binet),
    ("Simple matrix", fib_matrix),
    ("Fast Exponentiation", fib_fast_exp),
]

print("=" * 50)

for name, func in implementations:
    print(f"\n{name}")
    
    for test_n in test_values:
        elapsed = test_function(func, test_n)
        print(f"  n = {test_n}, time = {elapsed:.6f}")

