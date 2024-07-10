#FOR LOOP
rows=5
for i in range(rows+1):
     for j in range(i):
        print(j+1, end=" ")
     print()
# WHILE LOOP    
rows = 5
i = 0
while i <= rows:
    j = 0
    while j < i:
        print(j+1, end=" ")
        j += 1
    print()
    i += 1
    
        