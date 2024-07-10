#CREATE A FOLDER IN PRINT 10 TXT FILE
import os
def createfiles():
    a="c:\ht\ "
    folder_path = a+input("Enter the folder path: ")
    if not os.path.exists(folder_path):
        print("Folder does not exist. Creating a new folder...")
        os.makedirs(folder_path)
    
    for i in range(1, 11):
        file_name = f"file_{i}.txt"
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, "w") as f:
            f.write("harsh tilala")  # create an empty file
        print(f"File {file_name} created successfully!")

createfiles()