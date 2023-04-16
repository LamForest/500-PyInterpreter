import ipdb
import sys
def Fib(n):
    if n == 1:
        return 1
    
    if n == 0:
        return 1
    
    print(f1)
    f = sys._getframe()
    print("in Fib, ", f.f_globals)
    # import ipdb
    # ipdb.set_trace()
    
    return Fib(n-1) + Fib(n-2)


f = sys._getframe()
print(f.f_globals)
# ipdb.set_trace()
# f0 = Fib(0) #1
f1 = Fib(1) #1
f2 = Fib(2) #2
# f5 = Fib(5) #8
# f9 = Fib(9) # 55