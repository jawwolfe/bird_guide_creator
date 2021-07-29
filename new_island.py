import pyodbc


connection_string = "Driver={ODBC Driver 17 for SQL Server};"
connection_string += "Server=localhost\\SQLEXPRESS;"
connection_string += "Database=BirdGuide;"
connection_string += "Trusted_Connection=yes;"
conn = pyodbc.connect(connection_string)

path_occidental = 'C:\\Users\\Andrew\\PycharmProjects\\audioembedder\\NegrosOccidental.txt'
path_oriental = 'C:\\Users\\Andrew\\PycharmProjects\\audioembedder\\NegrosOriental.txt'


def process_file(path):
    a_file = open(path)
    file_contents = a_file.read()
    contents_split = file_contents.splitlines()
    my_list = []
    for item in contents_split:
        if 'sp.' not in item:
            if '/' not in item:
                if 'Domestic' not in item:
                    my_list.append(item.replace('\t', ''))

    return my_list


lst_negros_occidental = process_file(path_occidental)
lst_negros_oriental = process_file(path_oriental)
all = list(set(lst_negros_occidental + lst_negros_oriental))
ordered_all = []
c = 0
for item in lst_negros_oriental:
    c += 1
    dict_item = {c: item}
    ordered_all.append(dict_item)

for item in lst_negros_occidental:
    flag = False
    for diction in ordered_all:
        for key, value in diction.items():
            if item == value:
                flag = True
    if not flag:
        c += 1
        ordered_all.append({c: item})

sql = "Select BirdName from Birds;"
cursor = conn.cursor()
cursor.execute(sql)
birds = cursor.fetchall()
old_birds = []
for item in birds:
    old_birds.append(item[0])

c = 0
for new_bird in all:
    if new_bird not in old_birds:
        c += 1
        print(new_bird)
print(str(c))
