def add(*args):
    return sum(args)

def subtract(*args):
    result = args[0]
    for num in args[1:]:
        result -= num
    return result

def multiply(*args):
    result = 1
    for num in args:
        result *= num
    return result

def divide(*args):
    result = args[0]
    for num in args[1:]:
        if num == 0:
            return "Cannot divide by zero"
        result /= num
    return result

# Get multiple values from the user
nums = []
num_str = input("Enter numbers separated by space: ")
for num in num_str.split():
    nums.append(float(num))

# Display the options for arithmetic operations
print("Choose the arithmetic operation: 1) Add 2) Subtract 3) Multiply 4) Divide")

# Get the user's choice and perform the operation
choice = input("Enter your choice: ")

if choice == '1':
    result = add(*nums)
elif choice == '2':
    result = subtract(*nums)
elif choice == '3':
    result = multiply(*nums)
elif choice == '4':
    result = divide(*nums)
else:
    result = "Invalid choice"

# Display the result
print("Result:", result)
