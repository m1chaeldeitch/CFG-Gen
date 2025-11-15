def fib(m):
    f0 = 0
    f1 = 1
    f2 = None
    i = None

    if m <= 1:
        return m
    else:
        i = 2
        while i <= m:
            f2 = f0 + f1
            f0 = f1
            f1 = f2
            i = i + 1

        return f2

print fib(5)
