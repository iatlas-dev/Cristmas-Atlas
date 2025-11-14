import csv 

data = [["atlas","stefa"]]

with open('id.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerows(data)

with open('id.csv', 'r') as file:
    reader = csv.reader(file)
    datas = []
    for row in reader:
        print(row)
    
    