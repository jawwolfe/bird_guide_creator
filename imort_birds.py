from openpyxl import load_workbook
import os, glob, pyodbc, sys

path_root = 'C:/temp/'
path_audio = path_root + 'Optimized/'

connection_string = "Driver={ODBC Driver 17 for SQL Server};"
connection_string += "Server=localhost\\SQLEXPRESS;"
connection_string += "Database=BirdGuide;"
connection_string += "Trusted_Connection=yes;"
conn = pyodbc.connect(connection_string)


path = 'C:\\Users\\Andrew\\PycharmProjects\\audioembedder\\Clements_2019.xlsx'

path_my_name = 'C:/temp/Philippines Bird Guide/'

wb = load_workbook(path)
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


def get_scientific_name(bird_name, species):
    flag = False
    for species in species:
        if species['english'] == bird_name:
            flag = True
            return species['scientific']
    return ''


# First make sure all names are correct
os.chdir(path_audio)
for file in glob.glob('*'):
    full_name = file.rsplit(".", 1)[0]
    prefix = full_name[:3].strip()
    name = full_name[3:].strip()
    scientific = get_scientific_name(name, clements_species)
    if not scientific:
        # print(full_name)
        raise ValueError('No match on common name in Clements, check name')


for file in glob.glob('*'):
    full_name = file.rsplit(".", 1)[0]
    prefix = full_name[:3].strip()
    name = full_name[3:].strip()
    scientific = get_scientific_name(name, clements_species)
    if not scientific:
        raise ValueError('No match on common name in Clements, check name')
    sql = "Insert into Birds(BirdName, TaxanomicCode, ScientificName) values(?,?,?); Select @@Identity as 'ID';"
    params = (name, prefix, scientific)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    sql = "Select @@Identity as 'ID';"
    cursor.execute(sql)
    id = cursor.fetchone()[0]
    conn.commit()
    # default Cebu birds
    sql = 'Insert into BirdsIslands(BirdID, IslandID, ResidentStatusID) values(?, 1, 1);'
    params = (id)
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()

