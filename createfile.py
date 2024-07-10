import os
a="c:\ht\ "
fpath=a+input("Enter a path and file name to create a file :")
if os.path.exists(fpath):
    f1=open(fpath,"r")
    print(f1.read())
else:
    f1=open(fpath,"x")
    print("file creared")
    