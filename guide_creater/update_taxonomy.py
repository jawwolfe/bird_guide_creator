import pyodbc, string

connection_string = "Driver={ODBC Driver 17 for SQL Server};"
connection_string += "Server=localhost\\SQLEXPRESS;"
connection_string += "Database=BirdGuide;"
connection_string += "Trusted_Connection=yes;"
conn = pyodbc.connect(connection_string)

sql = "exec sp_get_clements_species;"
cursor = conn.cursor()
cursor.execute(sql)
data = cursor.fetchall()
conn.commit()
cursor.close()


let = list(string.ascii_uppercase[0:26])
let2 = list(string.ascii_uppercase[0:26])
letters = []
for l in let:
    for l2 in let2:
        letters.append(l + l2)
family_codes = []
for letter in let:
    for i in range(9):
        family_codes.append(letter + str(i+1))
c = 0
family = None
genus = None
g = 0
add_list = []

for item in data:
    if family != item[1]:
        family = item[1]
        #print(family)
        # create family prefix
        fpre = family_codes[c]
        c += 1
        #print(fpre)
        g = 0
        # create genus prefix
        gpre = letters[g]
    else:
        if genus != item[2]:
            genus = item[2]
            # increment g prefix
            g += 1
            gpre = letters[g]
        else:
            pass
    # create new item
    dict = {'order': item[0], 'group': family, 'code': fpre + gpre, 'english': item[3], 'scientific': item[4], 'range': ''}
    add_list.append(dict)

def search_list(list, needle):
    res = ''
    for item in list:
        if item['category'] == 'subspecies' or item['category'] == 'group (monotypic)':
            if needle in item['scientific']:
                sub = item['scientific'][item['scientific'].rindex(' ')+1:]
                res += (sub + ':  ' + item['range'] + '\n')
    return res

sql = "exec sp_get_clements_species_subspecies;"
cursor = conn.cursor()
cursor.execute(sql)
data = cursor.fetchall()
conn.commit()
cursor.close()

ranges = []
range = None
raw_data = []

for item in data:
    dict = {'category': item[2], 'range': item[5], 'scientific': item[6]}
    raw_data.append(dict)

for item in raw_data:
    if item['category'] == 'species':
        if item['range'] is None:
            if item['scientific'] == 'Crypturellus noctivagus':
                pass

            # this species has subspecies get all the ranges and ss name
            range = search_list(raw_data, item['scientific'])
        else:
            pass
            # this species has no subspecies just get range
            range = item['range']
        dict = {'scientific': item['scientific'], 'range': range}
        ranges.append(dict)

for add in add_list:
    for str_range in ranges:
        if add['scientific'] == str_range['scientific']:
            add['range'] = str_range['range']


for i in add_list:
    sql = 'exec sp_update_clements @order=?, @code=?, @english=?, @scientific=?, @ebirdgroup=?, @range=?'
    params = (i['order'], i['code'], i['english'], i['scientific'], i['group'], i['range'])
    cursor = conn.cursor()
    cursor.execute(sql, params)
    conn.commit()
    cursor.close()

conn.close()
pass
