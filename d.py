def fibo(n):
    a = 0 
    b = 1
    
    if n >= 1:
        print(a)  # Print first number (0)
    if n >= 2:
        print(b)  # Print second number (1)
    
    for i in range(2, n):
        c = a + b
        a = b
        b = c
        print(c)

fibo(10)  # Prints first 10 Fibonacci numbers

