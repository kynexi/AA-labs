from decimal import Decimal, getcontext

def fib(n):
    getcontext().prec = 60
    sqrt5 = Decimal(5).sqrt()
    phi = (Decimal(1) + sqrt5) / 2
    psi = (Decimal(1) - sqrt5) / 2
    return int((phi ** n - psi ** n) / sqrt5)
