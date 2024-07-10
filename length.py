def add(x, y):
    return x + y

def subtract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    return x / y if y != 0 else "Cannot divide by zero"

while True:
    # Get two values from the user
    num1 = float(input("Enter the first number: "))
    num2 = float(input("Enter the second number: "))

    # Display the options for arithmetic operations
    print("Choose the arithmetic operation:")
    print("1) Add")
    print("2) Subtract")
    print("3) Multiply")
    print("4) Divide")
    print("5) Exit")

    # Get the user's choice and perform the operation
    choice = input("Enter your choice (1/2/3/4/5): ")

    if choice == '1':
        result = add(num1, num2)
        print("Result:", result)
    elif choice == '2':
        result = subtract(num1, num2)
        print("Result:", result)
    elif choice == '3':
        result = multiply(num1, num2)
        print("Result:", result)
    elif choice == '4':
        result = divide(num1, num2)
        print("Result:", result)
    elif choice == '5':
        print("Exiting calculator...")
        break
    else:
        print("Invalid choice. Please enter a valid option (1/2/3/4/5).")
