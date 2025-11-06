from csv import reader

FILE_NAME = 'data.csv'


with open(FILE_NAME, 'r') as file:
    csv_reader = reader(file)
    content = list(csv_reader)
    col_names = content[1]
    data = content[2:]

print(col_names)
print(*data[:10], sep='\n')
