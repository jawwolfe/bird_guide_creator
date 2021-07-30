import pyodbc, csv, sys
from openpyxl import load_workbook


connection_string = "Driver={ODBC Driver 17 for SQL Server};"
connection_string += "Server=localhost\\SQLEXPRESS;"
connection_string += "Database=BirdGuide;"
connection_string += "Trusted_Connection=yes;"
conn = pyodbc.connect(connection_string)

path_occidental = 'C:\\Users\\Andrew\\PycharmProjects\\audioembedder\\NegrosOccidental.txt'
path_oriental = 'C:\\Users\\Andrew\\PycharmProjects\\audioembedder\\NegrosOriental.txt'
path_exotic = 'C:\\Users\\Andrew\\PycharmProjects\\audioembedder\\negros_exotic.xlsx'
path_clements = 'C:\\Users\\Andrew\\PycharmProjects\\audioembedder\\Clements_2019.xlsx'


def process_ebird_file(path):
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


wb = load_workbook(path_clements)
sheetname = "eBird Clements v2019 Aug 2019"
ws = wb[sheetname]
clements_data = []
clements_species = []
for row in ws.iter_rows(min_row=2, values_only=True):
     data = {'category': row[2], 'english': row[3], 'scientific': row[4]}
     clements_data.append(data)
for item in clements_data:
    if item['category'] == "species":
        bird = {'english': item['english'], 'scientific': item['scientific']}
        clements_species.append(bird)

lst_negros_occidental = process_ebird_file(path_occidental)
lst_negros_oriental = process_ebird_file(path_oriental)
all_ebird_birds = list(set(lst_negros_occidental + lst_negros_oriental))

wb = load_workbook(path_exotic)
sheetname = "Sheet1"
ws = wb[sheetname]

exotic_birds = []

for row in ws.iter_rows(min_row=2, values_only=True):
    if row[3]:
        data = {'name': row[2], 'scientific': row[3]}
        exotic_birds.append(data)

sql = "Select BirdName, TaxanomicCode, ScientificName from Birds;"
cursor = conn.cursor()
cursor.execute(sql)
old_birds = cursor.fetchall()

exotic_unmatched_old = []
for item in exotic_birds:
    flag = False
    for bird in old_birds:
        if bird[2].strip() == item['scientific'].strip():
            flag = True
    if not flag:
        # get english name from clements
        flag2 = False
        for taxon in clements_species:
            if taxon['scientific'].strip() == item['scientific'].strip():
                flag2 = True
                english = taxon['english']
            else:
                english = ''
        diction = {'name': item['name'], 'clements_name': english, 'scientific': item['scientific']}
        exotic_unmatched_old.append(diction)


master_ebird_list = []
for bird in all_ebird_birds:
    flag = False
    for item in old_birds:
        if bird.strip() == item[0].strip():
            flag = True
            add = {'code': item[1], 'name': item[0], 'scientific': item[2]}
    if not flag:
        # get scientific name from clements
        for taxon in clements_species:
            if taxon['english'].strip() == bird.strip():
                scien = taxon['scientific']
        add = {'code': '', 'name': bird, 'scientific': scien}
    master_ebird_list.append(add)


exotic_not_ebird = []
for exotic in exotic_birds:
    flag = False
    for ebird in master_ebird_list:
        if exotic['scientific'].strip() == ebird['scientific'].strip():
            flag = True
    if not flag:
        # get english name from clements
        flag2 = False
        for taxon in clements_species:
            if taxon['scientific'].strip() == exotic['scientific'].strip():
                flag2 = True
                english = taxon['english']
        # Get taxanomic code from old birds if exists
        flag3 = False
        for old in old_birds:
            if exotic['scientific'].strip() == old[2].strip():
                flag3 = True
                diction = {'code': old[1], 'name': english, 'scientific': exotic['scientific']}
                exotic_not_ebird.append(diction)
        if not flag3:
            diction = {'code': '', 'name': english, 'scientific': exotic['scientific']}
            exotic_not_ebird.append(diction)

all_negros = exotic_not_ebird + master_ebird_list

f = open("negros_all.csv", "w")
writer = csv.DictWriter(f, fieldnames=["code", "name", "scientific"], lineterminator='\n')
writer.writerows(all_negros)
f.close()

