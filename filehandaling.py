import os

while True:
    print("1. Append to a file")
    print("2. Create a file")
    print("3. Read a file")
    print("4. Remove a file")
    print("5. Write to a file")
    option = input("Enter your choice (1-5): ")
    file_path = input("Enter the file path: ")

    if option == '1':
        with open(file_path, 'a') as f: f.write(input("Enter content: ") + "\n")
    elif option == '2':
        with open(file_path, 'w') as f: f.write("")
    elif option == '3':
        try: print(open(file_path, 'r').read())
        except FileNotFoundError: print("File not found!")
    elif option == '4':
        try: os.remove(file_path)
        except FileNotFoundError: print("File not found!")
    elif option == '5':
        with open(file_path, 'w') as f: f.write(input("Enter content: ") + "\n")
    else: print("Invalid option. Please try again!")