# what is python ?
# features 
# applications of python.
# what is library in python.
# what is module in python.
# what is pvm in python ? (imp)
# How python works ?
# .py (source file) -> compiler ( it convert source file into byte .) -> pvm (it has an interpreter . it convert byte code into machine code) ->  processor (it excute machine code and display the result.)

# identifier ? name 
# variables -> is an identifier which are inter connected with memory location.

# check python is install or not  ( python --version )

# x = 10
# y = 10 
# # check memory location.
# print("x  : ",x, " ID : ", id(x))
# print("y  : ",x, " ID : ", id(y))



# data types
# price = 10.5
# age = 25
# city = "Delhi"
# isPass = True
# print("Price : ", price, " Type : ",type(price))
# print("age : ", age, " Type : ",type(age))
# print("city : ", city, " Type : ",type(city))
# print("isPass : ", isPass, " Type : ",type(isPass))

# Types of Data Type :-
# 1 Numeric data types :-  int, float, complex
# 2. Sequence data types :- string, list,tuple
# 3. set
# 4. map (dict)
# 5. bool
# 6. None

# int : it can be positive or negetive , n number of digits can we store into int data type.
# float : it can be positive or negetive . value should be in decimal form like(10.4,-10.7). 
# string :- we can create sting using double quotes or single quotes.
#           we can also create multile line string using triple single line quotes or triple double line quotes.
 
# name = "Deepak Kumar"
# city = 'New Delhi'
# though = """
#             this is first line
#             this is second line
#             so on...
# """

# though1 = '''
#             this is first line
#             this is second line
#             so on...
# '''
# print(city)


# mutable or immutable
# city = "New Delhi"
# # city[0] = "D"
# new_str = city.replace("New", "Dew")
# print(city)
# print(new_str)



# List :- 
# list is a mutable object
# list can store multi type values.
# represented by []
# duplicate value allow.
# indexing allow. [left (0 to n-1) or right (-1 to -n)]

# lst = [10,20,30,40]
# get first element using indexing 
# print(lst[0])
# print(lst[-1])  # Last element

# replace 10 to 100
# lst[0] = 100
# print(lst)

# remove 10 from list
# del lst[0]
# print(lst)

# remove 3o from list
# lst.pop(2)
# print(lst)

# remove last element from list
# lst.pop()
# print(lst)


# add an element at the last position.
# lst.append(900)
# print(lst)



# lst1 + lst2
# lst1 = [10,20,30,40]
# lst2 = [1,2,3,4]
# # print(lst1 + lst2)
# lst2.extend(lst1)
# print(lst2)


# list * 5 ( it will repeat the list obj)
# lst = [1,2,3,4]
# print(lst*5)



# print all elements through loop
# lst = [10,20,30,40]   #without indexing
# for i in lst:
#     print(i, end=" ")


# lst = [10,20,30,40]   #using indexing
# length = len(lst)
# # print(length)
# for i in range(0,length):
#     print(lst[i], end=" ")



# list comprehension
# perform any operation within a line.
# lst = [1,2,3,4]
# lst1 = []
# for i in lst:
#     result = i * i
#     lst1.append(result)

# print(lst1)
# lst = [1,2,3,4]
# new_lst = [i *i  for i in lst ]
# print(new_lst)




# tuple
# 1. immutable
# 2. it allow duplicate value
# 3. represented by ()
# 4. indexing allow
# 5. tup can store differ type values.
# 6. tup is faster than list.



# ==================== Day - 11 ======================


# set (completed by students)
# map - dict ()
# function -

# 1. create funtion
# def show():
#     print("show function...")

# show()


# 2. function with parameters
# here n1 and n2 are parameters
# def show(n1,n2):
#     print(n1 + n2)

# show(10,20)


# TypeError: show() missing 1 required positional argument: 'n2'
# def show(n1,n2):
#     print(n1 + n2)

# show(10)


# TypeError: show() takes 1 positional argument but 2 were given
# def show(n1):
#     print(n1)

# show(10,20)


# types of arguments 
# 1. formal arguments (parameters)
# 2. actual arguments show(10,20)

# or  we can devide
# 1. positional arguments
# 2. default arguments
# 3. variable length 
# 4. keyword variable length arguments
# 5. keyword aruguments.

# 1. positional arguments
# def show(n1,n2):
#     print(n1**n2)

# show(2,5)



# 5. keyword aruguments.
# def show(n1,n2):
#     print(n1**n2)

# show(n2=5,n1=2)



# 2. default arguments
# def show(n1,n2=5):
#     print(n1**n2)
# show(2,4)


# 3. variable length arguments (*args)
# it store value in tuple form
# *args should be tha last argument.

# def show(n1,n2,*args):
#     print(args)
#     sum = 0
#     for i in args:
#         sum += i
#     print(n1+ n2 +sum)
# show(2,4,5,10,40,30)



# 4. keyword variable length arguments (**kwargs)
# def show(**kwargs):
#     print(kwargs)
#     print(kwargs['a'] + kwargs['f'])
  
# show(a=2,b=4,c=5,d=10,e=40,f=30)




# decorator
# decorator is a function it takes func as an arguments and return function. 
# or we can say that , modify the other func functionality without using that function.



# def outerFun(fun):
#     print("Outer Function")
#     def innerFunc():
#         fun()
#         print("Inner Function")
#     return innerFunc

# @outerFun
# def myFun():
#     print("My Function")

# myFun()

# result = outerFun(myFun)
# result()







