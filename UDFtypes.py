#NO ARG NO RETURN
print("1 NO ARG NO RETURN")
def sum():
    print("Hello")
sum()

#WITH ARG NO RETURN
print("2 WITH ARG NO RETURN")
def sum(a,b):
    print(a+b)
sum(12,10)

#WITH ARG WITH RETURN
print("3 WITH ARG WITH RETURN")
def sum(a,b):
    return(a+b)
print(sum(10,20))
i=sum(10,30)
print(i)

#DEFAULT ARGUEMENT
print("4 DEFAULT ARGUEMENT")
def sum(a=12,b=12):
    return(a+b)
print(sum())
print(sum(100,200))

#variable length arguement
print("variable length arguement")
def sum(*arg):
    add =0
    for i in arg:
        add = add+ i
    return add
print(sum(10,20,30,40,50))
    

